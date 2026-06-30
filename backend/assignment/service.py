from sqlalchemy.ext.asyncio import AsyncSession
from sessions import repository as session_repository
from assignment import repository
from assignment.schema import (
    AssignmentCreateRequest,
    AssignmentUpdateRequest,
)
from sqlalchemy.exc import NoResultFound



from exceptions import NotFoundException

async def create_assignment(
    body: AssignmentCreateRequest,
    db: AsyncSession
):
    try:
        await session_repository.get_session_by_id(
            session_id=body.session_id,
            db=db
        )
    except NoResultFound:
        raise NotFoundException("Session not found")

    return await repository.create_assignment(
        db=db,
        body=body
    )


async def get_all_assignments(
    db: AsyncSession
):
    return await repository.get_all_assignments(
        db=db
    )


async def get_assignment_by_id(
    assignment_id: int,
    db: AsyncSession
):
    return await repository.get_assignment_by_id(
        assignment_id=assignment_id,
        db=db
    )


async def get_assignments_by_session_id(
    session_id: int,
    db: AsyncSession
):
    try:
        await session_repository.get_session_by_id(
            session_id=session_id,
            db=db
        )
    except NoResultFound:
        raise NotFoundException("Session not found")

    return await repository.get_assignments_by_session_id(
        session_id=session_id,
        db=db
    )


async def patch_assignment(
    assignment_id: int,
    body: AssignmentUpdateRequest,
    db: AsyncSession
):
    return await repository.patch_assignment(
        assignment_id=assignment_id,
        body=body,
        db=db
    )


async def delete_assignment(
    assignment_id: int,
    db: AsyncSession
):
    return await repository.delete_assignment(
        assignment_id=assignment_id,
        db=db
    )