from sqlalchemy import create_engine, Column
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
    date = Column("date")
    price = Column("price")


def insert_prices(data):
    with Session() as session:
        session.execute(insert(Prices), data)
        session.commit()


def truncate_prices():
    with Session() as session:
        session.execute(text("TRUNCATE TABLE btc.prices;"))
        session.commit()
