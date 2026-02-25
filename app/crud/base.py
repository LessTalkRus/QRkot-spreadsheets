from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def get(self, session: AsyncSession, obj_id: int):
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalars().first()

    async def get_multi(self, session: AsyncSession):
        result = await session.execute(
            select(self.model).order_by(self.model.id)
        )
        return list(result.scalars().all())

    async def create(
            self,
            session: AsyncSession,
            obj_in,
            user: Optional[User] = None
    ):
        obj_in_data = obj_in.model_dump()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.flush()
        return db_obj

    async def update(self, session: AsyncSession, db_obj, obj_in):
        obj_data = jsonable_encoder(db_obj)
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(
                exclude_unset=True
            )
        )

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        await session.flush()
        return db_obj

    async def remove(self, session: AsyncSession, db_obj):
        await session.delete(db_obj)
        await session.flush()
        return db_obj
