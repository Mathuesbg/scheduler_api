from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select

from scheduler_api.models import Booking


def booking_is_valid(booking, availabilities, session):
    selected_weekday = booking.day.strftime('%A').lower()
    # Check if the selected day is part of the user’s availability schedule
    user_schedule = [weekday.day for weekday in availabilities]

    if selected_weekday not in user_schedule:
        raise HTTPException(
            status_code=400, detail='Selected day is not available'
        )

    # the selected time slot must match an available slot exactly
    is_exact_match = any(
        available_slot.day == selected_weekday
        and available_slot.start == booking.slot.start
        and available_slot.end == booking.slot.end
        for available_slot in availabilities
    )

    if not is_exact_match:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The selected time slot is not available.',
        )

    # Check if the exact slot has already been booked
    is_booked = session.scalar(
        select(Booking).where(
            Booking.user_id == booking.user_id,
            Booking.day == booking.day,
            Booking.start == booking.slot.start,
        )
    )
    if is_booked:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Slot already booked.'
        )


def datetime_is_valid(date, start, end):
    # Validate if the booking slot has a valid time range
    if start >= end:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Invalid time range!'
        )

    # Validate if the selected day is in the past
    if date < datetime.today().date():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The selected day cannot be in the past.',
        )

    # Validate if the selected time is in the past (for today)
    cond1 = date == datetime.today().date()
    cond2 = start < datetime.now().time()

    if cond1 and cond2:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The selected time cannot be in the past.',
        )
