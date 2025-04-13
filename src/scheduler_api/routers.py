from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from . import schema
from .models import Availability, Booking, User
from .session import get_session

router = APIRouter()


# Users
@router.post(
    path='/users/',
    status_code=HTTPStatus.CREATED,
    response_model=schema.UserPublic,
)
def create_user(
    user: schema.UserCreate, session: Session = Depends(get_session)
):
    user_db = session.scalar(
        select(User).where(
            or_(User.username == user.username, User.email == user.email)
        )
    )

    if user_db:
        if user_db.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        if user_db.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

    user_db = User(username=user.username, email=user.email)
    session.add(user_db)
    session.commit()

    for date in user.availability:
        day = date.day

        for slot in date.slots:
            start = slot.start
            end = slot.end

            availability = Availability(
                user_id=user_db.id, day=day, start=start, end=end
            )
            session.add(availability)

    session.commit()

    session.refresh(user_db)

    return user_db


@router.post(
    path='/bookings/',
    status_code=HTTPStatus.CREATED,
    response_model=schema.BookingPublic,
)
def create_booking(
    booking: schema.BookingCreate, session: Session = Depends(get_session)
):
    if booking.day < datetime.today().date():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Invalid day!'
        )

    booked = session.scalar(
        select(Booking).where(
            Booking.user_id == booking.user_id,
            Booking.day == booking.day,
            Booking.start == booking.slot.start,
        )
    )

    if booked:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Invalid day!'
        )

    availabilities = session.scalars(
        select(Availability).where(Availability.user_id == booking.user_id)
    )

    booking_weekday = booking.day.strftime('%A').lower()
    if booking_weekday not in [x.day for x in availabilities]:
        raise HTTPException(status_code=400, detail='Invalid day!')

    if booking.slot.start >= booking.slot.end:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Invalid slot!'
        )

    cond1 = booking.day == datetime.today()
    cond2 = booking.slot.start < datetime.now().time()

    if cond1 and cond2:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='The selected time cannot be in the past.',
        )

    booked = session.scalar(
        select(Booking).where(
            Booking.user_id == booking.user_id,
            Booking.day == booking.day,
            (
                (booking.slot.start < Booking.end)
                & (booking.slot.end > Booking.start)
            ),
        )
    )
    if booked:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Time slot is already booked.',
        )

    availability = next(
        (a for a in availabilities if a.day == booking.day), None
    )
    if availability:
        valid = (
            availability.start <= booking.slot.start < availability.end
            and availability.start < booking.slot.end <= availability.end
        )
        if not valid:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='The time slot is not available.',
            )

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


@router.get(
    path="/slots/",
    response_model=schema.AvailableSlotsResponse
    )
def get_avaliable_slots(
    user_id: int, 
    day : str, 
    session : Session = Depends(get_session)
    ):
    
    try:
        day = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            detail="Invalid day"
        )
    
    user_db = session.scalar(
        select(User).where(User.id == user_id)
    )

    if not user_db:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            detail="Invalid user id"
        )

    weekday_str = day.strftime("%A").lower() 

    availabilities = session.scalars(
        select(Availability).where(
            (Availability.user_id == user_id)
            & (Availability.day == weekday_str)
        )
    ).all()

    bookeds = session.scalars(
        select(Booking).where(
            (Booking.user_id == user_id)
            & (Booking.day == day)
        )
    ).all()
    
    avaliables_slots = {"slots" : []}

    for slot in availabilities:

        is_booked = any(slot.start == booking.start for booking in bookeds)

        if not is_booked:
            avaliables_slots['slots'].append({"start": slot.start, "end": slot.end})


    return avaliables_slots