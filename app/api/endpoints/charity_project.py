from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.validators import (validate_full_amount_not_less_than_invested,
                                validate_project_can_be_deleted,
                                validate_project_exists,
                                validate_project_name_unique,
                                validate_project_name_unique_on_update,
                                validate_project_not_closed)
from app.core import current_superuser
from app.core.constants import SESSION_DEP
from app.crud.charity_project import charity_project_crud as crud
from app.models import Donation
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investment import invest_funds

router = APIRouter(
    prefix="/charity_project",
    tags=["Проекты для пожертвований"],
)


@router.get("/", response_model=list[CharityProjectDB])
async def get_projects(session: SESSION_DEP):
    """
    Получить список всех проектов.

    Проекты возвращаются в порядке возрастания `id`.

    **Ответ:** список объектов проекта.

    Пример ответа:
    ```json
    [
      {
        "id": 1,
        "name": "Корм для котят",
        "description": "Покупка корма для котят в приюте.",
        "full_amount": 5000,
        "invested_amount": 1200,
        "fully_invested": false,
        "create_date": "2026-02-06T12:00:00",
        "close_date": null
      }
    ]
    ```
    """
    return await crud.get_multi(session)


@router.post(
    "/",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def create_project(
    data: CharityProjectCreate,
    session: SESSION_DEP,
):
    """
    Создать новый благотворительный проект.

    Доступно только для суперпользователей.

    При создании проекта выполняется автоматическое инвестирование:
    - если в системе есть **незавершённые пожертвования**
    (с нераспределёнными средствами), они будут автоматически вложены в новый
    проект (по порядку поступления пожертвований).

    **Ошибки:**
    - `400` — если проект с таким именем уже существует.

    Пример запроса:
    ```json
    {
      "name": "Стерилизация котиков",
      "description": "Оплата стерилизации для бездомных котов.",
      "full_amount": 15000
    }
    ```
    """
    await validate_project_name_unique(crud, session, data.name)

    project = await crud.create(session, data)

    result = await session.execute(
        select(Donation)
        .where(Donation.fully_invested.is_(False))
        .order_by(Donation.create_date, Donation.id)
    )
    donations = list(result.scalars().all())

    invest_funds(project, donations)

    await session.commit()
    await session.refresh(project)
    return project


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: SESSION_DEP,
):
    """
    Частично обновить проект по `project_id`.

    Доступно только для суперпользователей.

    Доступные для изменения поля зависят от схемы `CharityProjectUpdate`.
    Обновление запрещено, если проект закрыт (`fully_invested = true`).

    Дополнительные правила валидации:
    - имя проекта должно оставаться уникальным;
    - нельзя установить `full_amount` меньше, чем уже инвестировано
    (`invested_amount`).

    **Ошибки:**
    - `404` — проект не найден;
    - `400` — проект закрыт;
    - `400` — новое имя не уникально;
    - `400` — `full_amount` меньше уже вложенной суммы.

    Пример запроса:
    ```json
    {
      "description": "Обновили описание проекта",
      "full_amount": 20000
    }
    ```
    """
    project = await crud.get(session, project_id)
    validate_project_exists(project)
    validate_project_not_closed(project)

    data = obj_in.model_dump(exclude_unset=True)

    if "name" in data:
        await validate_project_name_unique_on_update(
            crud,
            session,
            new_name=data["name"],
            current_name=project.name,
        )

    if "full_amount" in data:
        validate_full_amount_not_less_than_invested(
            new_full_amount=data["full_amount"],
            invested_amount=project.invested_amount,
        )

    for field, value in data.items():
        setattr(project, field, value)

    if project.invested_amount >= project.full_amount:
        project.fully_invested = True
        project.close_date = datetime.now()

    await session.commit()
    await session.refresh(project)
    return project


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_project(
    project_id: int,
    session: SESSION_DEP,
):
    """
    Удалить проект по `project_id`.

    Доступно только для суперпользователей.

    Удаление разрешено **только если**:
    - проект не закрыт (`fully_invested = false`);
    - и в проект не было вложено средств (`invested_amount = 0`).

    **Ошибки:**
    - `404` — проект не найден;
    - `400` — проект закрыт или в него уже инвестированы средства.

    Пример ошибки:
    ```json
    {
      "detail": "Нельзя удалить проект, т.к. были вложены средства."
    }
    ```
    """
    project = await crud.get(session, project_id)
    validate_project_exists(project)
    validate_project_can_be_deleted(project)

    await crud.remove(session, project)
    await session.commit()
    return project
