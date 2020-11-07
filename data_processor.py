import datetime
import os
import pandas as pd
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.sql import text

from db import engine, ads, brands, verticals

filepath = "/".join([os.getcwd(), "sample.csv"])


def batch_load_data():
    conn = engine.connect()
    df = pd.read_csv(filepath, usecols=[" VERTICAL", " BRAND"])
    deduplicated = df.drop_duplicates()
    for row in deduplicated.iterrows():
        _vertical_values = {
            "name": row[1][1].strip()
        }
        vertical_insert = insert(verticals).values(**_vertical_values)
        verticals_update = vertical_insert.on_duplicate_key_update(
            **_vertical_values)
        conn.execute(verticals_update)

        _brand_values = {
            "name": row[1][0].strip(),
            "vertical": conn.execute(
                verticals.select().where(
                    verticals.c.name == row[1][1].strip())).fetchone()[0]
        }
        brand_insert = insert(brands).values(**_brand_values)
        brands_update = brand_insert.on_duplicate_key_update(**_brand_values)
        conn.execute(brands_update)

    df = pd.read_csv(
        filepath,
        usecols=[
            "HOUSEHOLD_ID",
            " BRAND",
            " AD_SPOT_ID",
            " AD_DATE",
            " VIEW_DURATION"])
    for row in df.iterrows():
        conn.execute(ads.insert(), {
            "household_id": row[1][0],
            "brand": conn.execute(
                brands.select().where(
                    brands.c.name == row[1][1].strip())).fetchone()[0],
            "ad_spot_id": row[1][2],
            "ad_date": row[1][3].strip(),
            "view_duration": row[1][4],
        })


def validate_date_string(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def _filter_by_brands(statement, brands):
    if not isinstance(brands, tuple):
        raise TypeError("brands should be a tuple")
    _expression = (
        F"= '{brands[0]}'"
        if len(brands) == 1
        else F"IN {brands}")
    _and_stmt = F"AND b.name {_expression}"
    return text(" ".join([statement.text, _and_stmt]))


def _filter_by_household_ids(statement, household_ids):
    if not isinstance(household_ids, tuple):
        raise TypeError("household_ids should be a tuple")
    _expression = (
        F"= {household_ids[0]}"
        if len(household_ids) == 1
        else F"IN {household_ids}")
    _and_stmt = F"AND household_id {_expression}"
    return text(" ".join([statement.text, _and_stmt]))


def _filter_by_period(statement, date_from, date_to):
    if not isinstance(date_from, str) and not isinstance(date_to, str):
        raise TypeError("date_from and date_to should be strings")
    validate_date_string(date_from)
    validate_date_string(date_to)
    _and_stmt = F"AND ad_date BETWEEN '{date_from}' AND '{date_to}'"
    return text(" ".join([statement.text, _and_stmt]))


def get_number_of_ads_viewed(
        vertical,
        brands=None,
        date_from=None,
        date_to=None,
        household_ids=None):
    """
    Params
    ------
    - vertical (required)
    - brands - list of brand names (optional)
    - date_from - should be set if `date_to` is also set (optional)
    - date_to - should be set if `date_from` is also set (optional)
    - household_ids (optional)

    Output
    ------
    - Number of ads viewed
    """
    conn = engine.connect()
    statement = text(F"""
        SELECT COUNT(a.id) 
        FROM ads a
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v on b.vertical = v.id 
        WHERE v.name = '{str(vertical)}'
    """)
    if brands:
        statement = _filter_by_brands(statement, brands)
    if household_ids:
        statement = _filter_by_household_ids(statement, household_ids)
    if date_from and date_to:
        statement = _filter_by_period(statement, date_from, date_to)
    result = conn.execute(statement)
    return result.fetchone()[0]


def get_number_of_distinct_ads(
        vertical,
        brands=None,
        date_from=None,
        date_to=None,
        household_ids=None):
    """
    Params
    ------
    - vertical (required)
    - brands - list of brand names (optional)
    - date_from - should be set if `date_to` is also set (optional)
    - date_to - should be set if `date_from` is also set (optional)
    - household_ids (optional)

    Output
    ------
    - Number of distinct ads
    """
    conn = engine.connect()
    statement = text(F"""
        SELECT COUNT(DISTINCT a.ad_spot_id) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = '{str(vertical)}'
    """)
    if brands:
        statement = _filter_by_brands(statement, brands)
    if household_ids:
        statement = _filter_by_household_ids(statement, household_ids)
    if date_from and date_to:
        statement = _filter_by_period(statement, date_from, date_to)
    result = conn.execute(statement)
    return result.fetchone()[0]


def get_total_duration_of_ads_viewed_per_household(
        vertical,
        brands=None,
        date_from=None,
        date_to=None,
        household_ids=None):
    """
    Params
    ------
    - vertical (required)
    - brands - list of brand names (optional)
    - date_from - should be set if `date_to` is also set (optional)
    - date_to - should be set if `date_from` is also set (optional)
    - household_ids (optional)

    Output
    ------
    - Total Duration of ads viewed (distributed by household ids)
    """
    conn = engine.connect()
    statement = text(F"""
        SELECT a.household_id, SUM(a.view_duration) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = '{str(vertical)}'
    """)
    if brands:
        statement = _filter_by_brands(statement, brands)
    if household_ids:
        statement = _filter_by_household_ids(statement, household_ids)
    if date_from and date_to:
        statement = _filter_by_period(statement, date_from, date_to)

    statement = " ".join([statement.text, " GROUP BY 1;"])
    result = conn.execute(statement)
    return result.fetchall()
