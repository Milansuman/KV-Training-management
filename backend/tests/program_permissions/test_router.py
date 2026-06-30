"""HTTP-level tests for /program-permissions router."""

PROGRAM_PAYLOAD = {
    "title": "Freshers Training",
    "description": "Training for new joiners",
    "start_date": "2025-01-01",
    "end_date": "2025-06-30",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_admin(client):
    user = client.post("/auth/register", json={
        "username": "admin", "email": "admin@example.com",
        "display_name": "Admin", "password": "secret",
    }).json()
    token = client.post("/auth/login", json={
        "username_or_email": "admin", "password": "secret",
    }).cookies.get("access_token")
    return user["id"], token


def _create_program(client, token):
    return client.post(
        "/programs", json=PROGRAM_PAYLOAD, cookies={"access_token": token}
    ).json()["id"]


def _add_to_program(client, user_id, program_id, role="STAFF"):
    return client.post("/program-permissions", json={
        "user_id": user_id, "program_id": program_id, "role": role,
    })


# ---------------------------------------------------------------------------
# POST /program-permissions
# ---------------------------------------------------------------------------

def test_add_person_staff_returns_201(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)
    # create a second user to add (admin already has STAFF from program creation)
    member = client.post("/auth/register", json={
        "username": "member", "email": "member@example.com",
        "display_name": "Member", "password": "secret",
    }).json()

    response = _add_to_program(client, member["id"], program_id, "STAFF")

    assert response.status_code == 201
    assert response.json()["role"] == "STAFF"
    assert response.json()["user_id"] == member["id"]
    assert response.json()["program_id"] == program_id


def test_add_person_candidate_returns_201(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)
    member = client.post("/auth/register", json={
        "username": "member", "email": "member@example.com",
        "display_name": "Member", "password": "secret",
    }).json()

    response = _add_to_program(client, member["id"], program_id, "CANDIDATE")

    assert response.status_code == 201
    assert response.json()["role"] == "CANDIDATE"


def test_add_person_unknown_user_returns_404(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)

    response = _add_to_program(client, 99999, program_id)

    assert response.status_code == 404


def test_add_person_unknown_program_returns_404(client) -> None:
    user_id, token = _setup_admin(client)

    response = _add_to_program(client, user_id, 99999)

    assert response.status_code == 404


def test_add_person_duplicate_returns_409(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)
    member = client.post("/auth/register", json={
        "username": "member", "email": "member@example.com",
        "display_name": "Member", "password": "secret",
    }).json()

    _add_to_program(client, member["id"], program_id, "CANDIDATE")
    response = _add_to_program(client, member["id"], program_id, "CANDIDATE")

    assert response.status_code == 409


def test_add_person_invalid_role_returns_422(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)

    response = client.post("/program-permissions", json={
        "user_id": user_id, "program_id": program_id, "role": "SUPERADMIN",
    })

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /program-permissions/{permission_id}
# ---------------------------------------------------------------------------

def test_delete_permission_returns_204(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)
    member = client.post("/auth/register", json={
        "username": "member", "email": "member@example.com",
        "display_name": "Member", "password": "secret",
    }).json()
    permission_id = _add_to_program(client, member["id"], program_id, "CANDIDATE").json()["id"]

    response = client.delete(f"/program-permissions/{permission_id}")

    assert response.status_code == 204


def test_delete_permission_nonexistent_returns_404(client) -> None:
    response = client.delete("/program-permissions/99999")

    assert response.status_code == 404


def test_delete_permission_twice_returns_404(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)
    member = client.post("/auth/register", json={
        "username": "member", "email": "member@example.com",
        "display_name": "Member", "password": "secret",
    }).json()
    permission_id = _add_to_program(client, member["id"], program_id, "CANDIDATE").json()["id"]

    client.delete(f"/program-permissions/{permission_id}")
    response = client.delete(f"/program-permissions/{permission_id}")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /program-permissions/check
# ---------------------------------------------------------------------------

def test_check_returns_true_for_member(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)
    # admin already has STAFF permission from program creation
    response = client.get(f"/program-permissions/check?user_id={user_id}&program_id={program_id}")

    assert response.status_code == 200
    assert response.json()["is_member"] is True


def test_check_returns_false_for_non_member(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)
    other = client.post("/auth/register", json={
        "username": "other", "email": "other@example.com",
        "display_name": "Other", "password": "secret",
    }).json()

    response = client.get(f"/program-permissions/check?user_id={other['id']}&program_id={program_id}")

    assert response.status_code == 200
    assert response.json()["is_member"] is False


def test_check_returns_false_after_permission_deleted(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)
    member = client.post("/auth/register", json={
        "username": "member", "email": "member@example.com",
        "display_name": "Member", "password": "secret",
    }).json()
    permission_id = _add_to_program(client, member["id"], program_id, "CANDIDATE").json()["id"]

    client.delete(f"/program-permissions/{permission_id}")

    response = client.get(f"/program-permissions/check?user_id={member['id']}&program_id={program_id}")
    assert response.json()["is_member"] is False


def test_check_returns_false_for_unknown_user(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)

    response = client.get(f"/program-permissions/check?user_id=99999&program_id={program_id}")

    assert response.status_code == 200
    assert response.json()["is_member"] is False


# ---------------------------------------------------------------------------
# GET /program-permissions/program/{program_id}
# ---------------------------------------------------------------------------

def test_list_permissions_returns_200_with_members(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)

    member = client.post("/auth/register", json={
        "username": "member", "email": "member@example.com",
        "display_name": "Member", "password": "secret",
    }).json()

    client.post("/program-permissions", json={
        "user_id": member["id"], "program_id": program_id, "role": "CANDIDATE",
    })

    response = client.get(f"/program-permissions/program/{program_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # admin + member


def test_list_permissions_includes_user_info(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)

    response = client.get(f"/program-permissions/program/{program_id}")

    assert response.status_code == 200
    perm = response.json()[0]
    assert "permission_id" in perm
    assert "user_id" in perm
    assert "username" in perm
    assert "display_name" in perm
    assert "role" in perm


def test_list_permissions_excludes_deleted(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)

    member = client.post("/auth/register", json={
        "username": "member", "email": "member@example.com",
        "display_name": "Member", "password": "secret",
    }).json()

    perm_resp = client.post("/program-permissions", json={
        "user_id": member["id"], "program_id": program_id, "role": "CANDIDATE",
    })
    permission_id = perm_resp.json()["id"]

    # Delete the permission
    client.delete(f"/program-permissions/{permission_id}")

    response = client.get(f"/program-permissions/program/{program_id}")

    assert response.status_code == 200
    assert len(response.json()) == 1  # only admin remains


def test_list_permissions_empty_for_nonexistent_program(client) -> None:
    response = client.get("/program-permissions/program/99999")

    assert response.status_code == 200
    assert response.json() == []


def test_list_permissions_correct_roles(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token)

    member = client.post("/auth/register", json={
        "username": "member", "email": "member@example.com",
        "display_name": "Member", "password": "secret",
    }).json()

    client.post("/program-permissions", json={
        "user_id": member["id"], "program_id": program_id, "role": "CANDIDATE",
    })

    response = client.get(f"/program-permissions/program/{program_id}")

    assert response.status_code == 200
    data = response.json()
    roles = {p["username"]: p["role"] for p in data}
    assert roles["admin"] == "STAFF"
    assert roles["member"] == "CANDIDATE"
