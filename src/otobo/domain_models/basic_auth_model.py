from pydantic import BaseModel


class BasicAuth(BaseModel):
    UserLogin: str
    Password: str