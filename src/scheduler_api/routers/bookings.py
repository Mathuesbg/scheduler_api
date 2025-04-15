from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from scheduler_api import schema
from scheduler_api.database import get_session
from scheduler_api.models import Availability, Booking, User

router = APIRouter()


@router.post(
    path='/bookings/',
    status_code=HTTPStatus.CREATED,
    response_model=schema.BookingPublic,
)
def create_booking(
    booking: schema.BookingCreate, session: Session = Depends(get_session)
):
    # Validate if the selected day is in the past
    if booking.day < datetime.today().date():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The selected day cannot be in the past.',
        )

    # Validate if the booking slot has a valid time range
    if booking.slot.start >= booking.slot.end:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Invalid slot!'
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

    # Check if the selected day is part of the user’s availability schedule
    availabilities = session.scalars(
        select(Availability).where(Availability.user_id == booking.user_id)
    ).all()

    selected_weekday = booking.day.strftime('%A').lower()
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

    # Validate if the selected time is in the past (for today)
    cond1 = booking.day == datetime.today().date()
    cond2 = booking.slot.start < datetime.now().time()

    if cond1 and cond2:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The selected time cannot be in the past.',
        )

    # Booking Creation
    booking_obj = Booking(
        user_id=booking.user_id,
        client_name=booking.name,
        client_email=booking.email,
        day=booking.day,
        start=booking.slot.start,
        end=booking.slot.end,
    )

    session.add(booking_obj)
    session.commit()

    return {
        'message': 'Booking created successfully.',
        'booking': {
            'id': booking_obj.id,
            'day': booking_obj.day,
            'start': booking_obj.start,
            'end': booking_obj.end,
        },
    }


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
