from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.core.constants import (DATE_FORMAT, HOURS_IN_DAY, MINUTES_IN_HOUR,
                                SECONDS_IN_MINUTE, TABLE_VALUES)

SPREADSHEET_BODY_TEMPLATE = dict(
    properties=dict(
        title='Отчет на ...',
        locale='ru_RU'
    ),
    sheets=[dict(properties=dict(
        sheetType='GRID',
        sheetId=0,
        title='Список проектов',
        gridProperties=dict(
            rowCount=None,
            columnCount=None,
        )
    ))]
)


def format_time(time_in_days: float) -> str:
    days = int(time_in_days)
    fractional_day = time_in_days - days
    hours = int(fractional_day * HOURS_IN_DAY)
    minutes = int((fractional_day * HOURS_IN_DAY - hours) * MINUTES_IN_HOUR)
    seconds = int(((
        fractional_day * HOURS_IN_DAY - hours
    ) * MINUTES_IN_HOUR - minutes) * SECONDS_IN_MINUTE)
    if days > 1:
        return f'{days} days {hours:02d}:{minutes:02d}:{seconds:02d}'
    return f'{days} day, {hours:02d}:{minutes:02d}:{seconds:02d}'


async def format_data_report(projects):
    """
    Возвращает подготовленные данные для записи в таблицу.
    """
    table_values = deepcopy(TABLE_VALUES)
    table_values[0][1] = datetime.now().strftime(DATE_FORMAT)
    table_values.extend(
        list(project.values()) for project in projects
    )
    return table_values


async def spreadsheets_create(
    wrapper_service: Aiogoogle,
    spreadsheet_template: dict = SPREADSHEET_BODY_TEMPLATE,
):
    service = await wrapper_service.discover('sheets', 'v4')
    now_date_time = datetime.now().strftime(DATE_FORMAT)

    body = deepcopy(spreadsheet_template)
    body['properties']['title'] = f'Отчет на {now_date_time}'

    # rowCount/columnCount не выставляем
    grid_properties = body['sheets'][0]['properties'].get('gridProperties')
    if grid_properties:
        grid_properties.pop('rowCount', None)
        grid_properties.pop('columnCount', None)

    response = await wrapper_service.as_service_account(
        service.spreadsheets.create(json=body)
    )
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
    spreadsheet_id: str,
    wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=dict(
                type='user',
                role='writer',
                emailAddress=settings.email,
            ),
            fields='id'
        )
    )


async def spreadsheets_update_value(
    wrapper_services: Aiogoogle,
    spreadsheet_id: str,
    table_values: list,
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1',
            valueInputOption='USER_ENTERED',
            json=dict(
                majorDimension='ROWS',
                values=table_values
            )
        )
    )
