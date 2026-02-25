from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.core.constants import SESSION_DEP
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud as crud
from app.models import User
from app.models.charity_project import CharityProject
from app.schemas.donation import (DonationCreate, DonationFullInfoDB,
                                  DonationUserDB)
from app.services.investment import invest_funds

router = APIRouter(
    prefix="/donation",
    tags=["Пожертвования"],
)


@router.get(
    "/",
    response_model=list[DonationFullInfoDB],
    dependencies=[Depends(current_superuser)],
)
async def get_donations(session: SESSION_DEP):
    """
    Получить список всех пожертвований.

    Доступно только для суперпользователей.

    Возвращаются все пожертвования фонда в порядке их создания.
    В ответе содержится расширенная информация, включая суммы,
    распределённые по проектам.

    **Ответ:** список объектов пожертвований.

    Пример ответа:
    ```json
    [
      {
        "id": 0,
        "full_amount": 0,
        "comment": "string",
        "create_date": "2026-02-06T12:10:00",
        "user_id": 0,
        "invested_amount": 0,
        "fully_invested": true,
        "close_date": "2026-02-06T12:12:00"
      }
    ]
    ```
    """
    return await crud.get_multi(session)


@router.post(
    "/",
    response_model=DonationUserDB,
    response_model_exclude_none=True
)
async def create_donation(
    donation_in: DonationCreate,
    session: SESSION_DEP,
    user: Annotated[User, Depends(current_user)]
):
    """
    Создать новое пожертвование.

    Пожертвование автоматически распределяется по открытым проектам:
    средства инвестируются в самый старый незавершённый проект.
    Если средств больше, чем требуется текущему проекту,
    остаток инвестируется в следующий проект по порядку создания.

    Если на момент создания пожертвования нет открытых проектов,
    средства остаются нераспределёнными до появления нового проекта.

    Пример запроса:
    ```json
    {
      "full_amount": 5000,
      "comment": "Помощь приюту"
    }
    ```

    Пример ответа:
    ```json
    {
      "id": 3,
      "comment": "Помощь приюту",
      "full_amount": 5000,
      "invested_amount": 2000,
      "fully_invested": false,
      "create_date": "2026-02-06T12:20:00",
      "close_date": null
    }
    ```
    """
    donation = await crud.create(session, donation_in, user)

    result = await session.execute(
        select(CharityProject)
        .where(CharityProject.fully_invested.is_(False))
        .order_by(CharityProject.create_date, CharityProject.id)
    )
    projects = list(result.scalars().all())

    invest_funds(donation, projects)

    await session.commit()
    await session.refresh(donation)
    return donation


@router.get(
    '/my',
    response_model=list[DonationUserDB],
)
async def get_my_donations(
    session: SESSION_DEP,
    user: Annotated[User, Depends(current_user)]
):
    """Получает список всех пожертвований текущего пользователя."""
    return await crud.get_by_user(session, user)