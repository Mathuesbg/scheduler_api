from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from . import schema
from .models import Availability, User
from .session import get_session

router = APIRouter()


# Users
@router.post(
    path='/users/',
    status_code=HTTPStatus.CREATED,
    response_model=schema.UserPublic,
)
def create_user(
    user: schema.UserSchema, session: Session = Depends(get_session)
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
