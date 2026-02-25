from datetime import datetime
from typing import Iterable, List, TypeVar

TARGET = TypeVar("T")
SOURCE = TypeVar("S")


def invest_funds(target: TARGET, sources: Iterable[SOURCE]) -> List[SOURCE]:
    changed: List[SOURCE] = []
    now = datetime.now()

    for source in sources:
        if target.remaining == 0:
            if not target.fully_invested:
                target.fully_invested = True
                target.close_date = now
            break

        if source.remaining == 0:
            if not source.fully_invested:
                source.fully_invested = True
                source.close_date = now
            continue

        to_invest = min(target.remaining, source.remaining)

        target.invested_amount += to_invest
        source.invested_amount += to_invest

        for obj in (target, source):
            if obj.remaining == 0 and not obj.fully_invested:
                obj.fully_invested = True
                obj.close_date = now

        changed.append(source)

        if target.fully_invested:
            break

    return changed
