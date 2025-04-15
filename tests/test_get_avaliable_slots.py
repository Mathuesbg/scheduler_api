from datetime import date
from http import HTTPStatus


def test_get_avaliable_slots_response_withou_slots(client, booking):
    day = date.today()

    response = client.get(
        url=f'/slots/?user_id=1&day={day}',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'slots': []}


def test_get_avaliable_slots_returns_correctly_data_if_slots(client, user):
    day = date.today()

    response = client.get(
        url=f'/slots/?user_id=1&day={day}',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'slots': [{'start': '10:00:00', 'end': '10:40:00'}]
    }


def test_get_avaliable_slots_raise_exception_if_invalid_id(client, user):
    day = date.today()
    user_id = 1000
    response = client.get(
        url=f'/slots/?user_id={user_id}&day={day}',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Invalid user id'}


def test_get_avaliable_slots_raise_exception_if_invalid_date(client, user):
    day = date.today().strftime('%d/%m/%Y')

    response = client.get(
        url=f'/slots/?user_id=1&day={day}',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Invalid day'}
