def authenticate(client) -> None:
    client.post(
        "/auth/register",
        json={
            "username": "admin99999999",
            "display_name": "Admin User",
            "email": "admin@example.com",
            "password": "secret",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username_or_email": "admin99999999",
            "password": "secret",
        },
    )

    assert response.status_code == 200



def test_create_user_returns_created_user(client) -> None:
    authenticate(client)
    response = client.post(
        "/user",
        json={
            "username": "member",
            "display_name": "Member User",
            "email": "member@example.com",
            "password": "secret",
            "is_admin": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "member"
    assert response.json()["email"] == "member@example.com"


def test_get_user_by_id_returns_user(client) -> None:
    authenticate(client)

    create_response = client.post(
        "/user",
        json={
            "username": "member",
            "display_name": "Member User",
            "email": "member@example.com",
            "password": "secret",
            "is_admin": False,
        },
    )

    user_id = create_response.json()["id"]

    response = client.get(f"/user/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["username"] == "member"


def test_get_all_users_returns_user_list(client) -> None:
    authenticate(client)
    client.post(
        "/user",
        json={
            "username": "member",
            "display_name": "Member User",
            "email": "member@example.com",
            "password": "secret",
            "is_admin": False,
        },
    )

    response = client.get("/user")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    users = response.json()

    assert any(user["username"] == "member" for user in users)


def test_patch_user_updates_user_fields(client) -> None:
    authenticate(client)

    create_response = client.post(
        "/user",
        json={
            "username": "member",
            "display_name": "Member User",
            "email": "member@example.com",
            "password": "secret",
            "is_admin": False,
        },
    )

    user_id = create_response.json()["id"]

    response = client.patch(
        f"/user/{user_id}",
        json={"display_name": "Updated Member"},
    )

    assert response.status_code == 200
    assert response.json()["display_name"] == "Updated Member"