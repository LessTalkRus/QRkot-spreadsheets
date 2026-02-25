from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class CharityProjectBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    full_amount: PositiveInt


class CharityProjectCreate(CharityProjectBase):
    pass


class CharityProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1)
    full_amount: PositiveInt | None = None


class CharityProjectDB(CharityProjectBase):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: datetime | None = None
