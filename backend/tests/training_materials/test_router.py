from io import BytesIO
from unittest.mock import patch, MagicMock
from models.training_material import TrainingMaterial
from training_materials.constants import MaterialType

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


def test_upload_material_returns_material(client) -> None:
    authenticate_admin(client)
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env:
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        response = client.post(
            "/training-materials",
            data={
                "title": "Test Material",
                "session_id": 1,
                "user_id": 1,
            },
            files={
                "file": ("test.pdf", BytesIO(b"test content"), "application/pdf")
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Material"
        assert data["session_id"] == 1
        assert data["user_id"] == 1
        assert data["material_type"] == MaterialType.FILE.value


def test_upload_material_missing_file_returns_422(client) -> None:
    authenticate_admin(client)
    response = client.post(
        "/training-materials",
        data={
            "title": "Test Material",
            "session_id": 1,
            "user_id": 1,
        }
    )

    assert response.status_code == 422


def test_create_material_from_url_returns_material(client) -> None:
    authenticate_admin(client)
    response = client.post(
        "/training-materials/url",
        data={
            "title": "URL Material",
            "url": "https://example.com/resource",
            "session_id": 1,
            "user_id": 1,
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "URL Material"
    assert data["url"] == "https://example.com/resource"
    assert data["material_type"] == MaterialType.URL.value
    assert data["session_id"] == 1


def test_create_material_from_url_missing_url_returns_422(client) -> None:
    authenticate_admin(client)
    response = client.post(
        "/training-materials/url",
        data={
            "title": "URL Material",
            "session_id": 1,
            "user_id": 1,
        }
    )

    assert response.status_code == 422


def test_get_materials_returns_list(client) -> None:
    authenticate_admin(client)
    # Create some materials first
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env:
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        client.post(
            "/training-materials",
            data={
                "title": "Material 1",
                "session_id": 1,
                "user_id": 1,
            },
            files={
                "file": ("test1.pdf", BytesIO(b"content1"), "application/pdf")
            }
        )

        client.post(
            "/training-materials/url",
            data={
                "title": "Material 2",
                "url": "https://example.com",
                "session_id": 1,
                "user_id": 1,
            }
        )

    response = client.get("/training-materials")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_materials_returns_empty_list_initially(client) -> None:
    authenticate_admin(client)
    response = client.get("/training-materials")

    assert response.status_code == 200
    assert response.json() == []


def test_get_materials_by_session_id_returns_matching_materials(client) -> None:
    authenticate_admin(client)
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env:
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        client.post(
            "/training-materials",
            data={
                "title": "Session 1 Material",
                "session_id": 1,
                "user_id": 1,
            },
            files={
                "file": ("test1.pdf", BytesIO(b"content1"), "application/pdf")
            }
        )

        client.post(
            "/training-materials",
            data={
                "title": "Session 2 Material",
                "session_id": 2,
                "user_id": 1,
            },
            files={
                "file": ("test2.pdf", BytesIO(b"content2"), "application/pdf")
            }
        )

    response = client.get("/training-materials/1")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["session_id"] == 1


def test_get_materials_by_session_id_returns_404_for_missing_session(client) -> None:
    authenticate_admin(client)
    response = client.get("/training-materials/999")

    assert response.status_code == 404


def test_update_material_with_file_returns_updated_material(client) -> None:
    authenticate_admin(client)
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env, \
         patch("training_materials.service.delete_object"):
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        # Create material first
        create_response = client.post(
            "/training-materials",
            data={
                "title": "Original Title",
                "session_id": 1,
                "user_id": 1,
            },
            files={
                "file": ("test.pdf", BytesIO(b"content"), "application/pdf")
            }
        )

        material_id = create_response.json()["id"]

        # Update material
        response = client.put(
            f"/training-materials/{material_id}",
            data={
                "title": "Updated Title",
            },
            files={
                "file": ("updated.pdf", BytesIO(b"updated content"), "application/pdf")
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["material_type"] == MaterialType.FILE.value


def test_update_material_with_url_returns_updated_material(client) -> None:
    authenticate_admin(client)
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env, \
         patch("training_materials.service.delete_object"):
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        # Create material first
        create_response = client.post(
            "/training-materials",
            data={
                "title": "Original Title",
                "session_id": 1,
                "user_id": 1,
            },
            files={
                "file": ("test.pdf", BytesIO(b"content"), "application/pdf")
            }
        )

        material_id = create_response.json()["id"]

        # Update material with URL
        response = client.put(
            f"/training-materials/{material_id}",
            data={
                "title": "Updated Title",
                "url": "https://example.com/new-resource",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["url"] == "https://example.com/new-resource"
        assert data["material_type"] == MaterialType.URL.value


def test_update_material_returns_404_for_missing(client) -> None:
    authenticate_admin(client)
    response = client.put(
        "/training-materials/999",
        data={
            "title": "Updated Title",
        },
        files={
            "file": ("test.pdf", BytesIO(b"content"), "application/pdf")
        }
    )

    assert response.status_code == 404


def test_update_material_with_both_file_and_url_returns_400(client) -> None:
    authenticate_admin(client)
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env:
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        # Create material first
        create_response = client.post(
            "/training-materials",
            data={
                "title": "Original Title",
                "session_id": 1,
                "user_id": 1,
            },
            files={
                "file": ("test.pdf", BytesIO(b"content"), "application/pdf")
            }
        )

        material_id = create_response.json()["id"]

        # Try to update with both file and URL
        response = client.put(
            f"/training-materials/{material_id}",
            data={
                "title": "Updated Title",
                "url": "https://example.com/resource",
            },
            files={
                "file": ("test.pdf", BytesIO(b"content"), "application/pdf")
            }
        )

        assert response.status_code == 400


def test_update_material_with_no_file_or_url_returns_400(client) -> None:
    authenticate_admin(client)
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env:
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        # Create material first
        create_response = client.post(
            "/training-materials",
            data={
                "title": "Original Title",
                "session_id": 1,
                "user_id": 1,
            },
            files={
                "file": ("test.pdf", BytesIO(b"content"), "application/pdf")
            }
        )

        material_id = create_response.json()["id"]

        # Try to update with neither file nor URL
        response = client.put(
            f"/training-materials/{material_id}",
            data={
                "title": "Updated Title",
            }
        )

        assert response.status_code == 400


def test_delete_material_returns_success_message(client) -> None:
    authenticate_admin(client)
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env, \
         patch("training_materials.service.delete_object"):
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        # Create material first
        create_response = client.post(
            "/training-materials",
            data={
                "title": "Delete Me",
                "session_id": 1,
                "user_id": 1,
            },
            files={
                "file": ("test.pdf", BytesIO(b"content"), "application/pdf")
            }
        )

        material_id = create_response.json()["id"]

        # Delete material
        response = client.delete(f"/training-materials/{material_id}")

        assert response.status_code == 200
        assert response.json()["detail"] == "Training material deleted"


def test_delete_material_returns_404_for_missing(client) -> None:
    authenticate_admin(client)
    response = client.delete("/training-materials/999")

    assert response.status_code == 404


def test_delete_material_with_url_does_not_call_minio(client) -> None:
    authenticate_admin(client)
    # Create URL material
    client.post(
        "/training-materials/url",
        data={
            "title": "URL Material",
            "url": "https://example.com/resource",
            "session_id": 1,
            "user_id": 1,
        }
    )

    # Get material ID from the list
    response = client.get("/training-materials")
    material_id = response.json()[0]["id"]

    # Delete material
    with patch("training_materials.service.delete_object") as mock_delete:
        response = client.delete(f"/training-materials/{material_id}")

        assert response.status_code == 200
        mock_delete.assert_not_called()
