#!/usr/bin/python3

import os
import sqlalchemy
from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    Date,
    String,
    MetaData,
    ForeignKey,
    UniqueConstraint)


DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

engine = sqlalchemy.create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@localhost:3306/{DB_NAME}",
    echo=True
)

metadata = MetaData()


verticals = Table(
    "verticals",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "name",
        String(length=255),
        nullable=False,
        unique=True
    )
)


brands = Table(
    "brands",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(length=255), nullable=False),
    Column(
        "vertical",
        Integer,
        ForeignKey(
            "verticals.id",
            ondelete="RESTRICT",
            name="brand_vertical_pk_fkey"),
        nullable=False),
    UniqueConstraint("name", "vertical")
)


ads = Table(
    "ads",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("ad_spot_id", Integer, nullable=False),
    Column(
        "brand",
        Integer,
        ForeignKey(
            "brands.id",
            ondelete="RESTRICT",
            name="ad_brand_pk_fkey"
        ), nullable=False),
    Column("household_id", Integer, nullable=False),
    Column("ad_date", Date, nullable=False),
    Column("view_duration", BigInteger, nullable=False)
)


metadata.create_all(engine)
