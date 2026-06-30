import pytest
from datetime import datetime, UTC

from training_materials import repository
from models.training_material import TrainingMaterial
from training_materials.constants import MaterialType


@pytest.mark.asyncio
async def test_create_material_returns_material(db_session) -> None:
    material = TrainingMaterial(
        title="Python Basics",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    created = await repository.create_material(db=db_session, material=material)

    assert created.id is not None
    assert created.title == "Python Basics"
    assert created.material_type == MaterialType.FILE.value
    assert created.session_id == 1
    assert created.user_id == 1


@pytest.mark.asyncio
async def test_get_material_by_id_returns_materials_for_session(db_session) -> None:
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

    await repository.create_material(db=db_session, material=material1)
    await repository.create_material(db=db_session, material=material2)

    result = await repository.get_material_by_id(db=db_session, session_id=1)

    assert len(result) == 2
    assert all(m.session_id == 1 for m in result)


@pytest.mark.asyncio
async def test_get_material_by_id_returns_empty_for_missing_session(db_session) -> None:
    result = await repository.get_material_by_id(db=db_session, session_id=999)

    assert result == []


@pytest.mark.asyncio
async def test_get_material_by_id_excludes_deleted_materials(db_session) -> None:
    material = TrainingMaterial(
        title="Delete Me",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    created = await repository.create_material(db=db_session, material=material)
    created.deleted_at = datetime.now(UTC)
    await db_session.commit()

    result = await repository.get_material_by_id(db=db_session, session_id=1)

    assert result == []


@pytest.mark.asyncio
async def test_get_materials_returns_all_materials(db_session) -> None:
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
        session_id=2,
        user_id=2,
    )

    await repository.create_material(db=db_session, material=material1)
    await repository.create_material(db=db_session, material=material2)

    result = await repository.get_materials(db=db_session)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_materials_excludes_deleted(db_session) -> None:
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
        session_id=2,
        user_id=2,
    )

    created1 = await repository.create_material(db=db_session, material=material1)
    await repository.create_material(db=db_session, material=material2)

    # Delete first material
    created1.deleted_at = datetime.now(UTC)
    await db_session.commit()

    result = await repository.get_materials(db=db_session)

    assert len(result) == 1
    assert result[0].title == "Material 2"


@pytest.mark.asyncio
async def test_get_material_by_material_id_returns_material(db_session) -> None:
    material = TrainingMaterial(
        title="Specific Material",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    created = await repository.create_material(db=db_session, material=material)
    result = await repository.get_material_by_material_id(db=db_session, material_id=created.id)

    assert result.id == created.id
    assert result.title == "Specific Material"


@pytest.mark.asyncio
async def test_get_material_by_material_id_returns_none_for_missing(db_session) -> None:
    result = await repository.get_material_by_material_id(db=db_session, material_id=999)

    assert result is None


@pytest.mark.asyncio
async def test_get_material_by_material_id_returns_none_for_deleted(db_session) -> None:
    material = TrainingMaterial(
        title="Delete Me",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    created = await repository.create_material(db=db_session, material=material)
    created.deleted_at = datetime.now(UTC)
    await db_session.commit()

    result = await repository.get_material_by_material_id(db=db_session, material_id=created.id)

    assert result is None


@pytest.mark.asyncio
async def test_update_material_persists_changes(db_session) -> None:
    material = TrainingMaterial(
        title="Original Title",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    created = await repository.create_material(db=db_session, material=material)
    created.title = "Updated Title"
    created.url = "https://updated.com"

    updated = await repository.update_material(db=db_session, material=created)

    assert updated.title == "Updated Title"
    assert updated.url == "https://updated.com"
    assert updated.id == created.id


@pytest.mark.asyncio
async def test_delete_material_soft_deletes(db_session) -> None:
    material = TrainingMaterial(
        title="Delete Me",
        url="http://minio:9000/bucket/file.pdf",
        material_type=MaterialType.FILE.value,
        session_id=1,
        user_id=1,
    )

    created = await repository.create_material(db=db_session, material=material)
    assert created.deleted_at is None

    await repository.delete_material(db=db_session, material=created)

    # Verify it's still in DB but marked as deleted
    result = await repository.get_material_by_material_id(db=db_session, material_id=created.id)
    assert result is None

    # Directly check the DB to confirm deleted_at is set
    result_all = await repository.get_materials(db=db_session)
    assert len(result_all) == 0
