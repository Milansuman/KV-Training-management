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


# ---------------------------------------------------------------------------
# GET /user/{user_id}/program-status
# ---------------------------------------------------------------------------


def test_get_program_status_unauthenticated_returns_401(client) -> None:
    response = client.get("/user/1/program-status?program_id=1")
    assert response.status_code == 401


def test_get_program_status_non_admin_views_other_fails(client) -> None:
    authenticate_non_admin(client)

    # Get the admin user id
    response = client.get("/user")
    users = response.json()
    admin_user = next(u for u in users if u["username"] == "admin99999999")

    # Non-admin tries to view admin's status
    resp = client.get(f"/user/{admin_user['id']}/program-status?program_id=999")
    assert resp.status_code == 401


def test_get_program_status_self_succeeds_without_permissions(client) -> None:
    """A user can view their own program status even with no program permissions."""
    authenticate_non_admin(client)

    response = client.get("/user")
    users = response.json()
    non_admin = next(u for u in users if u["username"] == "nonadmin")
    user_id = non_admin["id"]

    resp = client.get(f"/user/{user_id}/program-status?program_id=999")
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_admin"] is False
    assert body["program_role"] is None
    assert body["session_roles"] == []


def test_get_program_status_admin_views_other_succeeds(client) -> None:
    """Admin can view another user's program status."""
    authenticate_non_admin(client)

    # Login as admin
    login_resp = client.post(
        "/auth/login",
        json={
            "username_or_email": "admin99999999",
            "password": "secret",
        },
    )
    assert login_resp.status_code == 200

    response = client.get("/user")
    users = response.json()
    non_admin = next(u for u in users if u["username"] == "nonadmin")
    non_admin_id = non_admin["id"]

    # Admin creates a program and adds the non-admin user
    program_resp = client.post(
        "/programs",
        json={
            "title": "Test Program",
            "description": "Test",
            "start_date": "2025-01-01",
            "end_date": "2025-06-30",
        },
    )
    assert program_resp.status_code == 201
    program_id = program_resp.json()["id"]

    # Add non-admin user to the program as CANDIDATE
    pp_resp = client.post(
        "/program-permissions",
        json={
            "user_id": non_admin_id,
            "program_id": program_id,
            "role": "CANDIDATE",
        },
    )
    assert pp_resp.status_code == 201

    # Create a session in the program
    from datetime import datetime, timezone, timedelta
    start = datetime.now(timezone.utc)
    session_resp = client.post(
        "/sessions",
        json={
            "title": "Test Session",
            "description": "A test session",
            "start_datetime": start.isoformat(),
            "end_datetime": (start + timedelta(hours=1)).isoformat(),
            "program_id": program_id,
        },
    )
    assert session_resp.status_code == 200
    session_id = session_resp.json()["id"]

    # Add session permission for the user
    sp_resp = client.post(
        "/session-permissions",
        json={
            "user_id": non_admin_id,
            "session_id": session_id,
            "role": "CANDIDATE",
        },
    )
    assert sp_resp.status_code == 201

    # Now admin views the non-admin's program status
    resp = client.get(f"/user/{non_admin_id}/program-status?program_id={program_id}")
    assert resp.status_code == 200
    body = resp.json()

    assert body["is_admin"] is False
    assert body["program_role"] == "CANDIDATE"
    assert len(body["session_roles"]) == 1
    assert body["session_roles"][0]["session_id"] == session_id
    assert body["session_roles"][0]["session_title"] == "Test Session"
    assert body["session_roles"][0]["role"] == "CANDIDATE"