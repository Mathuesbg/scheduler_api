from datetime import datetime
from http import HTTPStatus


def test_create_slot(client, user_today):
    weekday = datetime.today().strftime('%A').lower()

    response = client.post(
        url='/slots/',
        json={
            'user_id': user_today.id,
            'weekday': weekday,
            'slots': [{'start': '14:00', 'end': '14:40'}],
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'availabilities': [
            {
                'id': 1,
                'weekday': weekday,
                'slots': {'start': '10:00:00', 'end': '10:40:00'},
            },
            {
                'id': 2,
                'weekday': weekday,
                'slots': {'start': '14:00:00', 'end': '14:40:00'},
            },
        ]
    }


def test_create_slot_raises_if_invalid_id(client, user_today):
    weekday = datetime.today().strftime('%A').lower()
    user_id = 1000

    response = client.post(
        url='/slots/',
        json={
            'user_id': user_id,
            'weekday': weekday,
            'slots': [{'start': '14:00', 'end': '14:40'}],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Invalid user id'}


def test_create_slot_raises_if_overlaps_existing_slot(client, user_today):
    weekday = datetime.today().strftime('%A').lower()

    response = client.post(
        url='/slots/',
        json={
            'user_id': user_today.id,
            'weekday': weekday,
            'slots': [{'start': '09:50', 'end': '10:30'}],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'The time slot overlaps with an existing one'
    }


def test_create_slot_raises_if_exactmatch_any_existing_slot(
    client, user_today
):
    weekday = datetime.today().strftime('%A').lower()

    response = client.post(
        url='/slots/',
        json={
            'user_id': user_today.id,
            'weekday': weekday,
            'slots': [{'start': '10:00', 'end': '10:40'}],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'The time slot already exists'}


def test_create_slot_raises_if_invalid_time_range(
    client, user_today
):
    weekday = datetime.today().strftime('%A').lower()

    response = client.post(
        url='/slots/',
        json={
            'user_id': user_today.id,
            'weekday': weekday,
            'slots': [{'start': '10:00', 'end': '09:40'}],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Invalid time range!'}
