from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException


def date_is_valid(date, availabilities):
    # Validate if the selected day is in the past
    if date < datetime.today().date():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The selected day cannot be in the past.',
        )

    # Check if the selected day is part of the user’s availability schedule
    user_schedule = [weekday.day for weekday in availabilities]
    selected_weekday = date.strftime('%A').lower()

    if selected_weekday not in user_schedule:
        raise HTTPException(
            status_code=400, detail='Selected day is not available'
        )
