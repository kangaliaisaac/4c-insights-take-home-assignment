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
    - Number of distinct ads
    - Total Duration of ads viewed (distributed by household ids)
    """
    conn = engine.connect()
    statement = text(F"""
        SELECT COUNT(a.id) 
        FROM ads a
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v on b.vertical = v.id 
        WHERE v.name = '{str(vertical)}';
    """)
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
    - Number of ads viewed
    - Number of distinct ads
    - Total Duration of ads viewed (distributed by household ids)
    """
    conn = engine.connect()
    statement = text(F"""
        SELECT COUNT(DISTINCT a.ad_spot_id) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = '{str(vertical)}';
    """)
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
    - Number of ads viewed
    - Number of distinct ads
    - Total Duration of ads viewed (distributed by household ids)
    """
    conn = engine.connect()
    statement = text(F"""
        SELECT a.household_id, SUM(a.view_duration) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = '{str(vertical)}' GROUP BY 1;
    """)
    result = conn.execute(statement)
    return result.fetchall()
