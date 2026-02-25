from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):

    async def get_by_user(self, session, user: User):
        donations = await session.execute(
            select(Donation).where(Donation.user_id == user.id)
        )
        return list(donations.scalars().all())


donation_crud = CRUDDonation(Donation)
