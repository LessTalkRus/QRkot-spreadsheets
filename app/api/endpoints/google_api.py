from http import HTTPStatus

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import (GoogleAPIError,
                                    GoogleAuthError,
                                    get_service)
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.google_api import (format_data_report,
                                     format_time,
                                     set_user_permissions,
                                     spreadsheets_create,
                                     spreadsheets_update_value)

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service)
):
    """
    Сформировать Google-отчёт по закрытым благотворительным проектам.

    Доступно только суперпользователям.

    Эндпоинт создаёт Google Spreadsheet в Google Drive и заполняет его
    отчётом «Топ проектов по скорости закрытия».

    Алгоритм работы:
    1. Получаются завершённые проекты, отсортированные по скорости закрытия.
    2. Рассчитывается длительность сбора средств для каждого проекта.
    3. Формируется структура таблицы.
    4. Создаётся Google Spreadsheet через Google Drive API.
    5. Выдаются права доступа сервисному аккаунту.
    6. Таблица заполняется данными через Google Sheets API.
    7. Возвращается ссылка на созданный документ.

    Структура таблицы:
    - Дата формирования отчёта
    - Заголовок отчёта
    - Название проекта
    - Время сбора средств
    - Описание проекта

    Пример запроса:
    POST /google/
    Authorization: Bearer <superuser_token>

    Пример ответа:
    "https://docs.google.com/spreadsheets/d/1AbCDefGhIjKlMnOpQrStUvWxYz/edit"
    """
    try:
        table_body = await format_data_report(
            dict(
                name=project.name,
                time=format_time(project.time),
                description=project.description,
            ) for project in
            await charity_project_crud.get_projects_by_completion_rate(session)
        )

        spreadsheet_id, spreadsheet_url = await spreadsheets_create(
            wrapper_services
        )

        await set_user_permissions(spreadsheet_id, wrapper_services)
        try:
            await spreadsheets_update_value(
                wrapper_services,
                spreadsheet_id,
                table_body,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Некорректные данные для заполнения таблицы.",
            ) from e

        return spreadsheet_url
    except GoogleAuthError as e:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail='Ошибка аутентификации в Google API.',
        ) from e

    except GoogleAPIError as e:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail='Сервис Google временно недоступен.',
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Внутренняя ошибка сервера.',
        ) from e
