from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from scheduler_api import schema
from scheduler_api.database import get_session
from scheduler_api.models import Availability, Booking, User

router = APIRouter()


@router.get(path='/slots/', response_model=schema.AvailableSlotsResponse)
def get_avaliable_slots(
    user_id: int, day: str, session: Session = Depends(get_session)
):
    # Validates date format
    try:
        day = datetime.strptime(day, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail='Invalid day')

    # Validates user's id
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail='Invalid user id')

    # collecting bookings and availability for the selected date
    weekday_str = day.strftime('%A').lower()

    availabilities = session.scalars(
        select(Availability).where(
            (Availability.user_id == user_id)
            & (Availability.day == weekday_str)
        )
    ).all()

    bookeds = session.scalars(
        select(Booking).where(
            (Booking.user_id == user_id) & (Booking.day == day)
        )
    ).all()

    # collecting available bookings
    avaliables_slots = {'slots': []}

    for slot in availabilities:
        is_booked = any(slot.start == booking.start for booking in bookeds)

        if not is_booked:
            avaliables_slots['slots'].append({
                'start': slot.start,
                'end': slot.end,
            })

    return avaliables_slots
