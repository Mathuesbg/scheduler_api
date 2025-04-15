from http import HTTPStatus


def test_create_user_returns_201_if_valid_data(client):
    response = client.post(
        url='/users/',
        json={
            'username': 'Username',
            'email': 'email@email.com',
            'availability': [
                {
                    'day': 'monday',
                    'slots': [{'start': '11:50', 'end': '12:20'}],
                }
            ],
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'Username',
        'email': 'email@email.com',
    }


def test_create_user_raise_exception_if_username_already_exists(client, user):
    response = client.post(
        url='/users/',
        json={
            'username': 'UserTest',
            'email': 'email@email.com',
            'availability': [
                {
                    'day': 'monday',
                    'slots': [{'start': '11:50', 'end': '12:20'}],
                }
            ],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_raise_exception_if_email_already_exists(client, user):
    response = client.post(
        url='/users/',
        json={
            'username': 'Username',
            'email': 'test@mail.com',
            'availability': [
                {
                    'day': 'monday',
                    'slots': [{'start': '11:50', 'end': '12:20'}],
                }
            ],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}
