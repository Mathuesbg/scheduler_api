from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select

from scheduler_api.models import Booking


def booking_is_valid(booking, availabilities, session):
    # the selected time slot must match an available slot exactly
    selected_weekday = booking.day.strftime('%A').lower()

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
