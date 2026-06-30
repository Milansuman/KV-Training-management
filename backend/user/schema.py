from pydantic import BaseModel, ConfigDict, EmailStr

from models.program_permission import ProgramRoles
from models.session_permission import SessionRoles


class UserCreate(BaseModel):
    username: str
    display_name: str
    email: EmailStr
    password: str
    is_admin: bool


class UserUpdate(BaseModel):
    username: str | None = None
    display_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    is_admin: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    display_name: str
    email: EmailStr
    is_admin: bool


class SessionRoleInfo(BaseModel):
    session_id: int
    session_title: str
    role: SessionRoles | None


class UserProgramStatusResponse(BaseModel):
    is_admin: bool
    program_role: ProgramRoles | None
    session_roles: list[SessionRoleInfo]
