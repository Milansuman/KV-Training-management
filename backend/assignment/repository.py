from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import NotFoundException
from models.assignment import Assignment
from .schema import AssignmentCreateRequest, AssignmentUpdateRequest
from models.assignment_submission import AssignmentSubmission

async def create_assignment(
    db: AsyncSession,
    body: AssignmentCreateRequest
):

    db_assignment = Assignment(
        title=body.title.strip(),
        description=body.description.strip(),
        session_id=body.session_id,
        due_at=body.due_at
    )

    db.add(db_assignment)
    await db.commit()
    await db.refresh(db_assignment)

    return db_assignment


async def get_all_assignments(
    db: AsyncSession
):

    stmt = (
        select(Assignment)
        .where(Assignment.deleted_at.is_(None))
    )

    result = await db.scalars(stmt)

    return result.all()


async def get_assignment_by_id(
    assignment_id: int,
    db: AsyncSession
):

    stmt = (
        select(Assignment)
        .where(Assignment.deleted_at.is_(None))
        .where(Assignment.id == assignment_id)
    )

    result = await db.scalars(stmt)

    assignment = result.first()

    if not assignment:
        raise NotFoundException(
            detail="Assignment not found"
        )

    return assignment


async def get_assignments_by_session_id(
    session_id: int,
    db: AsyncSession
):

    stmt = (
        select(Assignment)
        .where(Assignment.deleted_at.is_(None))
        .where(Assignment.session_id == session_id)
        .order_by(Assignment.due_at)
    )

    result = await db.scalars(stmt)

    return result.all()


async def patch_assignment(
    assignment_id: int,
    body: AssignmentUpdateRequest,
    db: AsyncSession
):

    assignment = await get_assignment_by_id(
        assignment_id,
        db
    )

    update_data = body.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(assignment, field, value)

    assignment.updated_at = datetime.now(tz=UTC)

    await db.commit()
    await db.refresh(assignment)

    return assignment


from datetime import UTC, datetime
from sqlalchemy import update

async def delete_assignment(
    assignment_id: int,
    db: AsyncSession,
):
    assignment = await get_assignment_by_id(
        assignment_id,
        db,
    )

    now = datetime.now(tz=UTC)

    assignment.deleted_at = now

    stmt = (
        update(AssignmentSubmission)
        .where(AssignmentSubmission.assignment_id == assignment.id)
        .where(AssignmentSubmission.deleted_at.is_(None))
        .values(deleted_at=now)
    )

    await db.execute(stmt)
    await db.commit()
    await db.refresh(assignment)

    return assignment