from datetime import date, timedelta
from http import HTTPStatus

day = date.today() + timedelta(days=1)
day = day.strftime('%Y-%m-%d')


def test_create_booking_returns_201_and_correctly_data(client, user):
    response = client.post(
        url='/bookings/',
        json={
            'user_id': user.id,
            'name': 'testename',
            'email': 'user@example.com',
            'day': day,
            'slot': {'start': '10:00', 'end': '10:40'},
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'message': 'Booking created successfully.',
        'booking': {
            'id': 1,
            'day': day,
            'start': '10:00:00',
            'end': '10:40:00',
        },
    }


def test_create_booking_raises_if_date_is_in_the_past(client, user):
    today = date.today()
    day = today - timedelta(days=1)
    day = day.strftime('%Y-%m-%d')

    response = client.post(
        url='/bookings/',
        json={
            'user_id': user.id,
            'name': 'testename',
            'email': 'user@example.com',
            'day': day,
            'slot': {'start': '10:00', 'end': '10:40'},
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'The selected day cannot be in the past.'
    }


def test_create_booking_raises_if_end_is_less_or_equal_than_start(
    client, user
):
    response = client.post(
        url='/bookings/',
        json={
            'user_id': user.id,
            'name': 'testename',
            'email': 'user@example.com',
            'day': day,
            'slot': {'start': '10:00', 'end': '09:00'},
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Invalid slot!'}


def test_create_booking_raises_if_slot_already_booked(client, user, booking):
    response = client.post(
        url='/bookings/',
        json={
            'user_id': user.id,
            'name': 'testename',
            'email': 'user@example.com',
            'day': day,
            'slot': {'start': '10:00', 'end': '10:40'},
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Slot already booked.'}


def test_create_booking_raises_if_date_isnt_in_user_schedule(client, user):
    today = date.today()
    day = today + timedelta(days=2)
    day = day.strftime('%Y-%m-%d')

    response = client.post(
        url='/bookings/',
        json={
            'user_id': user.id,
            'name': 'testename',
            'email': 'user@example.com',
            'day': day,
            'slot': {'start': '10:00', 'end': '10:40'},
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Selected day is not available'}


def test_create_booking_raises_if_time_slot_doesnt_match(client, user):
    response = client.post(
        url='/bookings/',
        json={
            'user_id': user.id,
            'name': 'testename',
            'email': 'user@example.com',
            'day': day,
            'slot': {'start': '10:00', 'end': '10:39'},
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'The selected time slot is not available.'
    }


def test_create_booking_raises_if_time_slot_is_today_in_past(
    client, user_today
):
    day = date.today().strftime('%Y-%m-%d')

    response = client.post(
        url='/bookings/',
        json={
            'user_id': user_today.id,
            'name': 'testename',
            'email': 'user@example.com',
            'day': day,
            'slot': {'start': '10:00', 'end': '10:40'},
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'The selected time cannot be in the past.'
    }
