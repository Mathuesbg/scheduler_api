from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import or_, select

from scheduler_api.models import User


def user_is_valid(user, session):
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
