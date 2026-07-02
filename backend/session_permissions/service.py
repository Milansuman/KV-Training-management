from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from models.program_permission import ProgramRoles
from models.session import Session
from session_permissions.schema import SessionWithRoleResponse
from models.session_permission import SessionPermission, SessionRoles
from session_permissions import repository
from session_permissions.schema import SessionUserResponse

_STAFF_ALLOWED_ROLES = {SessionRoles.TRAINER, SessionRoles.MODERATOR, SessionRoles.CANDIDATE}
_CANDIDATE_ALLOWED_ROLES = {SessionRoles.CANDIDATE}


async def add_session_permission(
    db: AsyncSession,
    user_id: int,
    session_id: int,
    role: SessionRoles,
) -> SessionPermission:
    try:
        await repository.get_user_by_id(db=db, user_id=user_id)
    except NoResultFound as exc:
        raise NotFoundException("User not found") from exc

    try:
        session = await repository.get_session_by_id(db=db, session_id=session_id)
    except NoResultFound as exc:
        raise NotFoundException("Session not found") from exc

    program_permission = await repository.get_program_permission(
        db=db, user_id=user_id, program_id=session.program_id
    )

    if program_permission is None:
        raise ForbiddenException("User is not a member of this program")

    allowed_roles = (
        _STAFF_ALLOWED_ROLES
        if program_permission.role == ProgramRoles.STAFF
        else _CANDIDATE_ALLOWED_ROLES
    )

    if role not in allowed_roles:
        raise ForbiddenException(
            f"A {program_permission.role.value} can only be assigned roles: "
            f"{', '.join(r.value for r in allowed_roles)}"
        )

    existing = await repository.get_existing_session_permission(
        db=db, user_id=user_id, session_id=session_id
    )
    if existing:
        raise ConflictException("User already has a role in this session")

    try:
        return await repository.create_session_permission(
            db=db,
            user_id=user_id,
            session_id=session_id,
            role=role,
        )
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to add session permission") from exc


async def get_sessions_by_program(
    db: AsyncSession,
    program_id: int,
) -> list[Session]:
    try:
        return await repository.get_sessions_by_program_id(db=db, program_id=program_id)
    except SQLAlchemyError as exc:
        raise BadRequestException("Unable to fetch sessions") from exc


async def delete_session_permission(
    db: AsyncSession,
    permission_id: int,
) -> None:
    try:
        permission = await repository.get_session_permission_by_id(db=db, permission_id=permission_id)
    except NoResultFound as exc:
        raise NotFoundException("Session permission not found") from exc

    try:
        await repository.hard_delete_session_permission(db=db, permission=permission)
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to delete session permission") from exc


async def update_session_permission(
    db: AsyncSession,
    permission_id: int,
    role: SessionRoles,
) -> SessionPermission:
    try:
        permission = await repository.get_session_permission_by_id(db=db, permission_id=permission_id)
    except NoResultFound as exc:
        raise NotFoundException("Session permission not found") from exc

    try:
        session = await repository.get_session_by_id(db=db, session_id=permission.session_id)
    except NoResultFound as exc:
        raise NotFoundException("Session not found") from exc

    program_permission = await repository.get_program_permission(
        db=db, user_id=permission.user_id, program_id=session.program_id
    )

    if program_permission is None:
        raise ForbiddenException("User is not a member of this program")

    allowed_roles = (
        _STAFF_ALLOWED_ROLES
        if program_permission.role == ProgramRoles.STAFF
        else _CANDIDATE_ALLOWED_ROLES
    )

    if role not in allowed_roles:
        raise ForbiddenException(
            f"A {program_permission.role.value} can only be assigned roles: "
            f"{', '.join(r.value for r in allowed_roles)}"
        )

    try:
        return await repository.update_session_permission_role(db=db, permission=permission, role=role)
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to update session permission") from exc


async def get_session_permissions_by_program(
    db: AsyncSession,
    user_id: int,
    program_id: int,
) -> list[SessionWithRoleResponse]:
    try:
        rows = await repository.get_session_permissions_by_program_id(
            db=db, user_id=user_id, program_id=program_id
        )
    except SQLAlchemyError as exc:
        raise BadRequestException("Unable to fetch sessions") from exc

    return [
        SessionWithRoleResponse(
            id=session.id,
            title=session.title,
            description=session.description,
            start_datetime=session.start_datetime,
            end_datetime=session.end_datetime,
            program_id=session.program_id,
            created_at=session.created_at,
            updated_at=session.updated_at,
            role=role,
            permission_id=permission_id
        )
        for session, role, permission_id in rows
    ]


async def get_session_users(
    db: AsyncSession,
    session_id: int,
) -> list[SessionUserResponse]:
    try:
        rows = await repository.get_session_permissions_by_session_id(
            db=db, session_id=session_id
        )
    except SQLAlchemyError as exc:
        raise BadRequestException("Unable to fetch session users") from exc

    return [
        SessionUserResponse(
            id=permission.id,
            user_id=permission.user_id,
            session_id=permission.session_id,
            role=permission.role,
            display_name=user.display_name,
            email=user.email,
        )
        for permission, user in rows
    ]
