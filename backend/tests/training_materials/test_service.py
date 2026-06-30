import pytest
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile

from training_materials import service
from exceptions import BadRequestException, NotFoundException
from models.training_material import TrainingMaterial
from training_materials.constants import MaterialType


@pytest.fixture
def mock_upload_file():
    """Create a mock UploadFile for testing."""
    file = MagicMock(spec=UploadFile)
    file.filename = "test.pdf"
    file.content_type = "application/pdf"
    file.read = AsyncMock(return_value=b"test file content")
    return file


@pytest.mark.asyncio
async def test_upload_material_creates_material(db_session, mock_upload_file) -> None:
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env:
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        result = await service.upload_material(
            db=db_session,
            title="Test Material",
            session_id=1,
            user_id=1,
            file=mock_upload_file,
        )

        assert result.title == "Test Material"
        assert result.session_id == 1
        assert result.user_id == 1
        assert result.material_type == MaterialType.FILE.value
        assert "http://minio:9000/test-bucket/" in result.url
        mock_client.put_object.assert_called_once()


@pytest.mark.asyncio
async def test_upload_material_calls_minio_put_object(db_session, mock_upload_file) -> None:
    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env:
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        await service.upload_material(
            db=db_session,
            title="Test Material",
            session_id=1,
            user_id=1,
            file=mock_upload_file,
        )

        mock_client.put_object.assert_called_once()
        call_kwargs = mock_client.put_object.call_args[1]
        assert call_kwargs["bucket_name"] == "test-bucket"
        assert call_kwargs["content_type"] == "application/pdf"
        assert call_kwargs["length"] == len(b"test file content")


@pytest.mark.asyncio
async def test_create_material_from_url_creates_url_material(db_session) -> None:
    result = await service.create_material_from_url(
        db=db_session,
        title="URL Material",
        url="https://example.com/resource",
        session_id=1,
        user_id=1,
    )

    assert result.title == "URL Material"
    assert result.url == "https://example.com/resource"
    assert result.material_type == MaterialType.URL.value
    assert result.session_id == 1
    assert result.user_id == 1


@pytest.mark.asyncio
async def test_get_materials_returns_all_materials(db_session) -> None:
    # Create test materials
    material1 = TrainingMaterial(
        title="Material 1",
        url="http://minio:9000/bucket/file1.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )
    material2 = TrainingMaterial(
        title="Material 2",
        url="https://example.com",
        material_type=MaterialType.URL.value,
        session_id=1,
        user_id=1,
    )

    db_session.add(material1)
    db_session.add(material2)
    await db_session.commit()

    result = await service.get_materials(db=db_session)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_material_returns_materials_for_session(db_session) -> None:
    # Create test materials
    material = TrainingMaterial(
        title="Test Material",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    db_session.add(material)
    await db_session.commit()

    result = await service.get_material(db=db_session, session_id=1)

    assert len(result) == 1
    assert result[0].title == "Test Material"


@pytest.mark.asyncio
async def test_get_material_raises_not_found_for_missing_session(db_session) -> None:
    with pytest.raises(NotFoundException):
        await service.get_material(db=db_session, session_id=999)


@pytest.mark.asyncio
async def test_update_material_with_file_replaces_content(db_session, mock_upload_file) -> None:
    # Create initial material
    material = TrainingMaterial(
        title="Original Title",
        url="http://minio:9000/bucket/old-file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    db_session.add(material)
    await db_session.commit()

    with patch("training_materials.service.client") as mock_client, \
         patch("training_materials.service.env") as mock_env, \
         patch("training_materials.service.delete_object") as mock_delete:
        mock_env.MINIO_BUCKET = "test-bucket"
        mock_env.MINIO_ENDPOINT = "minio:9000"

        result = await service.update_material(
            db=db_session,
            material_id=material.id,
            title="Updated Title",
            file=mock_upload_file,
        )

        assert result.title == "Updated Title"
        assert result.material_type == MaterialType.FILE.value
        mock_delete.assert_called_once_with("old-file.pdf")
        mock_client.put_object.assert_called_once()


@pytest.mark.asyncio
async def test_update_material_with_url_replaces_content(db_session) -> None:
    # Create initial material
    material = TrainingMaterial(
        title="Original Title",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    db_session.add(material)
    await db_session.commit()

    with patch("training_materials.service.delete_object") as mock_delete:
        result = await service.update_material(
            db=db_session,
            material_id=material.id,
            title="Updated Title",
            url="https://example.com/new-resource",
        )

        assert result.title == "Updated Title"
        assert result.url == "https://example.com/new-resource"
        assert result.material_type == MaterialType.URL.value
        mock_delete.assert_called_once_with("file.pdf")


@pytest.mark.asyncio
async def test_update_material_raises_bad_request_for_both_file_and_url(db_session, mock_upload_file) -> None:
    material = TrainingMaterial(
        title="Original",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    db_session.add(material)
    await db_session.commit()

    with pytest.raises(BadRequestException):
        await service.update_material(
            db=db_session,
            material_id=material.id,
            title="Updated",
            file=mock_upload_file,
            url="https://example.com",
        )


@pytest.mark.asyncio
async def test_update_material_raises_bad_request_for_no_file_or_url(db_session) -> None:
    material = TrainingMaterial(
        title="Original",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    db_session.add(material)
    await db_session.commit()

    with pytest.raises(BadRequestException):
        await service.update_material(
            db=db_session,
            material_id=material.id,
            title="Updated",
        )


@pytest.mark.asyncio
async def test_update_material_raises_not_found_for_missing(db_session, mock_upload_file) -> None:
    with pytest.raises(NotFoundException):
        await service.update_material(
            db=db_session,
            material_id=999,
            title="Updated",
            file=mock_upload_file,
        )


@pytest.mark.asyncio
async def test_delete_material_removes_file_from_minio(db_session) -> None:
    material = TrainingMaterial(
        title="Delete Me",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    db_session.add(material)
    await db_session.commit()

    with patch("training_materials.service.delete_object") as mock_delete:
        await service.delete_material(
            db=db_session,
            material_id=material.id,
        )

        mock_delete.assert_called_once_with("file.pdf")


@pytest.mark.asyncio
async def test_delete_material_does_not_remove_url_from_minio(db_session) -> None:
    material = TrainingMaterial(
        title="Delete Me",
        url="https://example.com/resource",
        material_type=MaterialType.URL.value,
        session_id=1,
        user_id=1,
    )

    db_session.add(material)
    await db_session.commit()

    with patch("training_materials.service.delete_object") as mock_delete:
        await service.delete_material(
            db=db_session,
            material_id=material.id,
        )

        mock_delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_material_raises_not_found_for_missing(db_session) -> None:
    with pytest.raises(NotFoundException):
        await service.delete_material(
            db=db_session,
            material_id=999,
        )
