from sqlalchemy import create_engine, Column, select, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, insert

import os

engine = create_engine(
    f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:5432/{os.environ['DB_NAME']}"
)
Base = declarative_base()

Session = sessionmaker(bind=engine)


class Prices(Base):
    __tablename__ = "prices"
    __table_args__ = {"schema": "btc"}
    id = Column("id", primary_key=True)
    date = Column(Date)
    price = Column("price")


class Analysis(Base):
    __tablename__ = "analysis"
    __table_args__ = {"schema": "btc"}
    date = Column(Date, primary_key=True)
    price = Column("price")
    signal = Column("signal")


class Gains(Base):
    __tablename__ = "gains"
    __table_args__ = {"schema": "btc"}
    id = Column("id", primary_key=True)
    realized_gain = Column("realized_gain")
    unrealized_gain = Column("unrealized_gain")


def pull_data():
    with Session() as session:
        data = session.execute(select(Prices).order_by(Prices.date)).scalars().all()
    return data


def insert_analysis(analysis):
    with Session() as session:
        session.execute(text("TRUNCATE TABLE btc.analysis;"))
        session.execute(
            insert(Analysis), analysis["data"]
        )
        session.commit()
