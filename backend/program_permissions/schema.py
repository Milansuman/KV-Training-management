from pydantic import BaseModel, ConfigDict, field_validator

from models.program_permission import ProgramRoles


class AddPersonRequest(BaseModel):
    user_id: int
    program_id: int
    role: ProgramRoles

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: object) -> ProgramRoles:
        allowed = {r.value for r in ProgramRoles}
        if isinstance(value, str) and value.upper() not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return value  # type: ignore[return-value]


class ProgramPermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    program_id: int
    role: ProgramRoles


class UpdatePersonRequest(BaseModel):
    role: ProgramRoles

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: object) -> ProgramRoles:
        allowed = {r.value for r in ProgramRoles}
        if isinstance(value, str) and value.upper() not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return value  # type: ignore[return-value]


class UserInProgramResponse(BaseModel):
    is_member: bool


class ProgramPermissionUserResponse(BaseModel):
    """Permission response with the user's display info included."""
    model_config = ConfigDict(from_attributes=True)

    permission_id: int
    user_id: int
    username: str
    display_name: str
    role: ProgramRoles
