from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException


def time_is_valid(date, start, end):
    # Validate if the booking slot has a valid time range
    if start >= end:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Invalid slot!'
        )

    # Validate if the selected time is in the past (for today)
    cond1 = date == datetime.today().date()
    cond2 = start < datetime.now().time()

    if cond1 and cond2:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The selected time cannot be in the past.',
        )
