from fastapi import HTTPException, status


def raise_project_not_found() -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Проект не найден.",
    )


def validate_project_exists(project) -> None:
    if not project:
        raise_project_not_found()


def validate_project_not_closed(project) -> None:
    if project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя редактировать закрытый проект.",
        )


def raise_project_name_not_unique() -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Имя проекта должно быть уникальным.",
    )


async def validate_project_name_unique(
    crud,
    session,
    name: str,
) -> None:
    if await crud.get_by_name(session, name):
        raise_project_name_not_unique()


async def validate_project_name_unique_on_update(
    crud,
    session,
    new_name: str,
    current_name: str,
) -> None:
    if new_name != current_name and await crud.get_by_name(session, new_name):
        raise_project_name_not_unique()


def validate_full_amount_not_less_than_invested(
    new_full_amount: int,
    invested_amount: int,
) -> None:
    if new_full_amount < invested_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Полная сумма не может быть меньше уже вложенной суммы.",
        )


def validate_project_can_be_deleted(project) -> None:
    if project.fully_invested or project.invested_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить проект, т.к. были вложены средства.",
        )
