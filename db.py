#!/usr/bin/python3

import os
import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base


DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

engine = sqlalchemy.create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@localhost:3306/{DB_NAME}",
    echo=True
)
Base = declarative_base()


class Vertical(Base):
    __tablename__ = "vertical"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(length=255), nullable=False)


class Brand(Base):
    __tablename__ = "brand"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(length=255), nullable=False)
    vertical = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey(
            Vertical.__tablename__ + ".id",
            ondelete="RESTRICT",
            name="brand_vertical_id_fkey"),
        nullable=False)

    sqlalchemy.UniqueConstraint("name", "vertical")


class Ad(Base):
    __tablename__ = "ad"

    ad_spot_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    brand = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey(
            Brand.__tablename__ + ".id",
            ondelete="RESTRICT",
            name="ad_brand_id_fkey"
        ),
        nullable=False)
    household_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    ad_date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    view_duration = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False)


Base.metadata.create_all(engine)

Session = sqlalchemy.orm.session.sessionmaker()
Session.configure(bind=engine)
session = Session()
