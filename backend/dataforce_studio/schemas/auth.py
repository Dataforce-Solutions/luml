from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None


class UserInfo(BaseModel):
    email: EmailStr
    full_name: str
    photo_url: str | None = None
