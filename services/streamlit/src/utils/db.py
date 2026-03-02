from sqlalchemy import create_engine, Column, select, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, insert
import pandas as pd

import os

engine = create_engine(
    f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:5432/{os.environ['DB_NAME']}"
)
Base = declarative_base()

Session = sessionmaker(bind=engine)


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
        analysis = pd.read_sql(session.query(Analysis).statement, session.bind)
        gains = pd.read_sql(session.query(Gains).statement, session.bind)
    return analysis, gains
