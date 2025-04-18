from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from scheduler_api.database import get_session
from scheduler_api.models import Availability, Booking
from scheduler_api.schema import BookingCreate, BookingPublic
from scheduler_api.validators import booking_validator

router = APIRouter()


@router.post(
    path='/bookings/',
    status_code=HTTPStatus.CREATED,
    response_model=BookingPublic,
)
def create_booking(
    booking: BookingCreate, session: Session = Depends(get_session)
):
    availabilities = session.scalars(
        select(Availability).where(Availability.user_id == booking.user_id)
    ).all()

    booking_validator.datetime_is_valid(
        booking.day, booking.slot.start, booking.slot.end
    )

    booking_validator.booking_is_valid(booking, availabilities, session)

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
