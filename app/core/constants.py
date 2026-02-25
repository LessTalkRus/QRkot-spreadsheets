from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session

SESSION_DEP = Annotated[AsyncSession, Depends(get_async_session)]
NAME_LENGTH = 100
TOKEN_LIFTIME_SECONDS = 3600
MIN_PASSWORD_LENGTH = 3

SPREADSHEET_URL = 'https://www.googleapis.com/auth/spreadsheets'
DRIVE_URL = 'https://www.googleapis.com/auth/drive'
DATE_FORMAT = '%Y/%m/%d %H:%M:%S'
ROWS_LIMIT = 200
COLUMNS_LIMIT = 10

TABLE_VALUES = [
    ['Отчёт от', None],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание проекта']
]