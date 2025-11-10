from typing import Literal, TypeAlias

from pydantic import BaseModel, Field

BooleanInteger: TypeAlias = Literal[0, 1]


class UserModel(BaseModel):
    """Model for OTOBO/Znuny user configuration."""
    user_name: str = Field(default="", description="Login name of the user")
    first_name: str = Field(default="", description="First name of the user")
    last_name: str = Field(default="", description="Last name of the user")
    email: str = Field(default="", description="Email address of the user")
    password: str = Field(default="", description="Password for the user")
    groups: list[str] = Field(default_factory=list, description="Groups to assign to the user")


class GroupConfig(BaseModel):
    """Model for OTOBO/Znuny group configuration."""
    name: str = Field(..., description="Name of the group")
    comment: str | None = Field(default=None, description="Optional comment for the group")


class QueueConfig(BaseModel):
    """Model for OTOBO/Znuny queue configuration."""
    name: str = Field(..., description="Name of the queue")
    group: str = Field(..., description="Group that owns the queue")
    system_address_id: int | None = Field(default=None, description="System address identifier")
    system_address_name: str | None = Field(default=None, description="System address name")
    comment: str | None = Field(default=None, description="Optional comment for the queue")
    unlock_timeout: int | None = Field(default=None, description="Unlock timeout in minutes")
    first_response_time: int | None = Field(default=None, description="First response time in minutes")
    update_time: int | None = Field(default=None, description="Update time in minutes")
    solution_time: int | None = Field(default=None, description="Solution time in minutes")
    calendar: int | None = Field(default=None, description="Calendar identifier")
