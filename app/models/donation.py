from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import InvestedBase


class Donation(InvestedBase):
    __tablename__ = "donation"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user'),
        nullable=True
    )
