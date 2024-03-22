from fastapi_do_zero.schemas import UserPublic


def test_root_deve_retornar_200_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'message': 'Olá mundo'}


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == 200
    assert 'access_token' in token
    assert 'token_type' in token


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret123',
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_create_user_already_exist(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'Teste',
            'email': 'batatinha@frita.com',
            'password': '123mudeiagora',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'Username já cadastrado.'}


def test_read_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == 200
    assert response.json() == {'users': [user_schema]}


def test_read_user_specific(client, user):
    response = client.get('/users/1')

    assert response.status_code == 200
    assert response.json() == {
        'username': 'Teste',
        'email': 'teste@teste.com',
        'id': 1,
    }


def test_read_user_specific_not_found(client):
    response = client.get('/users/1')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Usuário não encontrado.'}


def test_udpate_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@sponja.com',
            'password': 'mudeinoteste',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@sponja.com',
        'id': 1,
    }


def test_update_user_not_exist(client, user, token):
    response = client.put(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@sponja.com',
            'password': 'mudeinoteste',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Não tem permissão para executar essa função.'
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'Usuário deletado com sucesso.'}


def test_delete_user_not_exist(client, token):
    response = client.delete(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Não tem permissão para executar essa função.'
    }
