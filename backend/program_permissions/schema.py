from pydantic import BaseModel, ConfigDict, field_validator

from models.program_permission import ProgramRoles


class AddPersonRequest(BaseModel):
    user_id: int
    program_id: int
    role: ProgramRoles

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: str) -> ProgramRoles:
        allowed = {r.value for r in ProgramRoles}
        if isinstance(value, str) and value.upper() not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return value


class ProgramPermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    program_id: int
    role: ProgramRoles


class UserInProgramResponse(BaseModel):
    is_member: bool
