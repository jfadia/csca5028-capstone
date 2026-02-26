from pydantic import BaseModel, validator, BeforeValidator, AfterValidator
from datetime import datetime
from typing import Annotated

DateTimeStr = Annotated[
    datetime,
    BeforeValidator(lambda v: datetime.strptime(v, "%Y-%m-%d")),
    AfterValidator(lambda v: v.replace(hour=0, minute=0, second=0)),
]


class CollectData(BaseModel):
    start_date: DateTimeStr
    end_date: DateTimeStr

    @validator("start_date", "end_date")
    def validate_date(cls, value):
        assert value <= datetime.today(), "Date must be in the past"
        return value
