def test_create_user_returns_created_user(client) -> None:
    response = client.post(
        "/user",
        json={
            "username": "admin",
            "display_name": "Admin User",
            "email": "admin@example.com",
            "password": "secret",
            "is_admin": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "admin"
    assert response.json()["email"] == "admin@example.com"


def test_get_user_by_id_returns_user(client) -> None:
    create_response = client.post(
        "/user",
        json={
            "username": "admin",
            "display_name": "Admin User",
            "email": "admin@example.com",
            "password": "secret",
            "is_admin": False,
        },
    )

    user_id = create_response.json()["id"]
    response = client.get(f"/user/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["username"] == "admin"


def test_get_all_users_returns_user_list(client) -> None:
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
    assert len(response.json()) == 1


def test_patch_user_updates_user_fields(client, db_session) -> None:
    create_response = client.post(
        "/user",
        json={
            "username": "admin",
            "display_name": "Admin User",
            "email": "admin@example.com",
            "password": "secret",
            "is_admin": False,
        },
    )

    user_id = create_response.json()["id"]
    response = client.patch(
        f"/user/{user_id}",
        json={"display_name": "Updated Admin"},
    )

    assert response.status_code == 200
    assert response.json()["display_name"] == "Updated Admin"
