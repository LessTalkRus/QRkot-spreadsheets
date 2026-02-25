from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_by_name(self, session: AsyncSession, name: str):
        result = await session.execute(
            select(CharityProject).where(CharityProject.name == name)
        )
        return result.scalars().first()

    async def get_projects_by_completion_rate(
            self, session: AsyncSession
    ):
        time_delta = (
            func.julianday(CharityProject.close_date) -
            func.julianday(CharityProject.create_date)
        )
        return (
            await session.execute(
                select(
                    CharityProject.name,
                    time_delta.label('time'),
                    CharityProject.description,
                ).where(
                    CharityProject.fully_invested == 1
                ).order_by(time_delta.label('time'))
            )
        ).all()


charity_project_crud = CRUDCharityProject(CharityProject)
