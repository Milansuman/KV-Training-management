def authenticate_admin(client) -> None:
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


def authenticate_non_admin(client) -> None:
    # First user registered gets admin, so register that one first
    client.post(
        "/auth/register",
        json={
            "username": "admin99999999",
            "display_name": "Admin User",
            "email": "admin@example.com",
            "password": "secret",
        },
    )

    # Second user registered gets non-admin
    client.post(
        "/auth/register",
        json={
            "username": "nonadmin",
            "display_name": "Non-Admin User",
            "email": "nonadmin@example.com",
            "password": "secret",
        },
    )

    # Login as the non-admin user
    response = client.post(
        "/auth/login",
        json={
            "username_or_email": "nonadmin",
            "password": "secret",
        },
    )

    assert response.status_code == 200


def test_create_user_returns_created_user(client) -> None:
    authenticate_admin(client)
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


def test_create_user_non_admin_fails(client) -> None:
    authenticate_non_admin(client)
    response = client.post(
        "/user",
        json={
            "username": "another",
            "display_name": "Another User",
            "email": "another@example.com",
            "password": "secret",
            "is_admin": False,
        },
    )

    assert response.status_code == 401


def test_get_user_by_id_returns_user_unauthenticated(client) -> None:
    # First create a user (needs admin auth)
    authenticate_admin(client)
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

    # Clear cookies to test unauthenticated access
    client.cookies.clear()

    response = client.get(f"/user/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["username"] == "member"


def test_get_all_users_returns_user_list_unauthenticated(client) -> None:
    authenticate_admin(client)
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

    client.cookies.clear()
    response = client.get("/user")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    users = response.json()
    assert any(user["username"] == "member" for user in users)


def test_patch_user_self_succeeds(client) -> None:
    authenticate_non_admin(client)
    
    # Get all users to find our ID
    response = client.get("/user")
    users = response.json()
    non_admin_user = next(u for u in users if u["username"] == "nonadmin")
    user_id = non_admin_user["id"]

    # Patch our own display name
    patch_response = client.patch(
        f"/user/{user_id}",
        json={"display_name": "Updated Non-Admin"},
    )

    assert patch_response.status_code == 200
    assert patch_response.json()["display_name"] == "Updated Non-Admin"


def test_patch_user_other_fails_for_non_admin(client) -> None:
    # Register admin and non-admin
    authenticate_non_admin(client)
    
    response = client.get("/user")
    users = response.json()
    admin_user = next(u for u in users if u["username"] == "admin99999999")
    admin_id = admin_user["id"]

    # Non-admin tries to patch admin
    patch_response = client.patch(
        f"/user/{admin_id}",
        json={"display_name": "Hack Admin Name"},
    )

    assert patch_response.status_code == 401


def test_patch_user_other_succeeds_for_admin(client) -> None:
    authenticate_non_admin(client)
    response = client.get("/user")
    users = response.json()
    non_admin_user = next(u for u in users if u["username"] == "nonadmin")
    non_admin_id = non_admin_user["id"]

    # Log in as admin
    login_response = client.post(
        "/auth/login",
        json={
            "username_or_email": "admin99999999",
            "password": "secret",
        },
    )
    assert login_response.status_code == 200

    # Admin patches non-admin
    patch_response = client.patch(
        f"/user/{non_admin_id}",
        json={"display_name": "Admin Updated This"},
    )

    assert patch_response.status_code == 200
    assert patch_response.json()["display_name"] == "Admin Updated This"


def test_delete_user_self_succeeds(client) -> None:
    authenticate_non_admin(client)
    
    response = client.get("/user")
    users = response.json()
    non_admin_user = next(u for u in users if u["username"] == "nonadmin")
    user_id = non_admin_user["id"]

    # Delete our own user
    delete_response = client.delete(f"/user/{user_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == user_id


def test_delete_user_other_fails_for_non_admin(client) -> None:
    authenticate_non_admin(client)
    
    response = client.get("/user")
    users = response.json()
    admin_user = next(u for u in users if u["username"] == "admin99999999")
    admin_id = admin_user["id"]

    # Non-admin tries to delete admin
    delete_response = client.delete(f"/user/{admin_id}")

    assert delete_response.status_code == 401


def test_delete_user_other_succeeds_for_admin(client) -> None:
    authenticate_non_admin(client)
    response = client.get("/user")
    users = response.json()
    non_admin_user = next(u for u in users if u["username"] == "nonadmin")
    non_admin_id = non_admin_user["id"]

    # Log in as admin
    login_response = client.post(
        "/auth/login",
        json={
            "username_or_email": "admin99999999",
            "password": "secret",
        },
    )
    assert login_response.status_code == 200

    # Admin deletes non-admin
    delete_response = client.delete(f"/user/{non_admin_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == non_admin_id