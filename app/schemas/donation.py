from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class DonationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_amount: PositiveInt
    comment: str | None = Field(default=None)


class DonationDB(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    full_amount: int
    comment: str | None = None
    create_date: datetime
    user_id: Optional[int] = None


class DonationFullInfoDB(DonationDB):
    invested_amount: int
    fully_invested: bool
    close_date: datetime | None = None


class DonationUserDB(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    full_amount: int
    comment: str | None = None
    create_date: datetime
