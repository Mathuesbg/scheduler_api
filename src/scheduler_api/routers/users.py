from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from scheduler_api import schema
from scheduler_api.database import get_session
from scheduler_api.models import Availability, User
from scheduler_api.validators import users_validator

router = APIRouter()


@router.post(
    path='/users/',
    status_code=HTTPStatus.CREATED,
    response_model=schema.UserPublic,
)
def create_user(
    user: schema.UserCreate, session: Session = Depends(get_session)
):
    users_validator.user_is_valid(user, session)

    # User Creation
    new_user = User(username=user.username, email=user.email)
    session.add(new_user)
    session.commit()

    # Availabities Creation
    for date in user.availability:
        day = date.day

        for slot in date.slots:
            start = slot.start
            end = slot.end

            availability = Availability(
                user_id=new_user.id, day=day, start=start, end=end
            )
            session.add(availability)

    session.commit()
    session.refresh(new_user)

    return new_user
