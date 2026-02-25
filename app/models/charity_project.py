from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import NAME_LENGTH
from app.models.base_model import InvestedBase


class CharityProject(InvestedBase):
    __tablename__ = "charityproject"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(NAME_LENGTH), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
