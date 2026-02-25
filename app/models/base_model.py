from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class InvestedBase(Base):
    __abstract__ = True

    full_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    invested_amount: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    fully_invested: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    close_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    @property
    def remaining(self) -> int:
        return int(self.full_amount) - int(self.invested_amount)
