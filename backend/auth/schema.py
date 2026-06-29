from pydantic import BaseModel, ConfigDict, EmailStr

class TokenPayload(BaseModel):
    sub: str
    type: str
    username: str
    email: str
    display_name: str
    is_admin: bool


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    display_name: str
    password: str


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class GoogleAuthRequest(BaseModel):
    id_token: str


class GoogleHandshakeRequest(BaseModel):
    nonce: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    display_name: str
    is_admin: bool


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str