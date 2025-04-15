from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from scheduler_api import schema
from scheduler_api.database import get_session
from scheduler_api.models import Availability, User

router = APIRouter()


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

    # Validate if user credentials are unique
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

    # User Creation
    user_db = User(username=user.username, email=user.email)
    session.add(user_db)
    session.commit()

    # Availabities Creation
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
