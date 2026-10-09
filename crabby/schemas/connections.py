from datetime import datetime
import re
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class HeaderItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    key: str = Field(..., min_length=1, max_length=256)
    value: str = Field(..., min_length=1, max_length=8192)

    @field_validator("key")
    @classmethod
    def validate_header_key(cls, value: str) -> str:
        if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", value):
            raise ValueError("Header names must contain only valid HTTP token characters.")
        if value.casefold() in {"host", "content-length", "transfer-encoding", "connection"}:
            raise ValueError("This header is managed by the HTTP client and cannot be overridden.")
        return value

    @field_validator("value")
    @classmethod
    def reject_header_newlines(cls, value: str) -> str:
        if "\r" in value or "\n" in value or "\x00" in value:
            raise ValueError("Header values cannot contain control characters.")
        return value


class ConnectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: Literal["ollama"] = Field("ollama")
    host: str = Field(..., min_length=1, max_length=2048)
    headers: List[HeaderItem] = Field(default_factory=list)
    timeout: float = Field(30.0, ge=0.5, le=300)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Connection name cannot be empty.")
        return value

    @field_validator("headers")
    @classmethod
    def validate_unique_headers(cls, value: List[HeaderItem]) -> List[HeaderItem]:
        keys = [header.key.casefold() for header in value]
        if len(keys) != len(set(keys)):
            raise ValueError("Header names must be unique.")
        return value


class ConnectionCreate(ConnectionBase):
    pass


class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    headers: Optional[List[HeaderItem]] = None
    timeout: Optional[float] = None


class ConnectionResponse(ConnectionBase):
    id: str
    created_at: str
    updated_at: str
    models: List[str] = Field(default_factory=list)


class PaginatedConnectionsResponse(BaseModel):
    items: List[ConnectionResponse]
    total: int
    page: int
    size: int
    pages: int
