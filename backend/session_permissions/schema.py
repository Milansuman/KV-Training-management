from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from models.session_permission import SessionRoles


class AddSessionPermissionRequest(BaseModel):
    user_id: int
    session_id: int
    role: SessionRoles

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: str) -> SessionRoles:
        allowed = {r.value for r in SessionRoles}
        if isinstance(value, str) and value.upper() not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return SessionRoles(value)


class SessionPermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    session_id: int
    role: SessionRoles


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    program_id: int
    created_at: datetime
    updated_at: datetime


class UpdateSessionPermissionRequest(BaseModel):
    role: SessionRoles

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: str) -> SessionRoles:
        allowed = {r.value for r in SessionRoles}
        if isinstance(value, str) and value.upper() not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return SessionRoles(value)


class SessionWithRoleResponse(BaseModel):
    id: int
    permission_id: int | None
    title: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    program_id: int
    created_at: datetime
    updated_at: datetime
    role: SessionRoles | None


class SessionUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    session_id: int
    role: SessionRoles
    display_name: str
    email: str
