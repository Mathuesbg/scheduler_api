from datetime import datetime, time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from scheduler_api.app import app
from scheduler_api.database import get_session
from scheduler_api.models import Availability, Base, Booking, User


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    yield session
    session.close()


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user(session):
    user = User(
        username='UserTest',
        email='test@mail.com',
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    start = time(hour=10)
    end = time(hour=10, minute=40)
    day = datetime.today().strftime('%A').lower()

    availabilities = Availability(
        user_id=user.id, day=day, start=start, end=end
    )
    session.add(availabilities)
    session.commit()

    return user


@pytest.fixture
def booking(user, session):
    booking = Booking(
        user_id=user.id,
        client_name='usertest',
        client_email='user@test.com',
        day=datetime.today().date(),
        start=time(hour=10),
        end=time(hour=10, minute=40),
    )

    session.add(booking)
    session.commit()

    return booking
