from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class HeaderItem(BaseModel):
    key: str
    value: str


class ConnectionBase(BaseModel):
    name: str = Field(...)
    type: Literal["ollama"] = Field("ollama")
    host: str = Field(...)
    headers: List[HeaderItem] = Field(default_factory=list)
    timeout: float = Field(30.0)


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
