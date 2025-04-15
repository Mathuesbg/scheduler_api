from datetime import date, timedelta
from http import HTTPStatus

day = date.today() + timedelta(days=1)
day = day.strftime('%Y-%m-%d')


def test_get_avaliable_slots_response_withou_slots(client, booking):
    response = client.get(
        url=f'/slots/?user_id=1&day={day}',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'slots': []}


def test_get_avaliable_slots_returns_correctly_data_if_slots(client, user):
    response = client.get(
        url=f'/slots/?user_id=1&day={day}',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'slots': [{'start': '10:00:00', 'end': '10:40:00'}]
    }


def test_get_avaliable_slots_raise_exception_if_invalid_id(client, user):
    user_id = 1000
    response = client.get(
        url=f'/slots/?user_id={user_id}&day={day}',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Invalid user id'}


def test_get_avaliable_slots_raise_exception_if_invalid_date(client, user):
    day = date.today() + timedelta(days=2)
    day = day.strftime('%d-%m-%Y')
    response = client.get(
        url=f'/slots/?user_id=1&day={day}',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Invalid day'}
