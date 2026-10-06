from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class HeaderItem(BaseModel):
    key: str = Field(...)
    value: str = Field(...)


class MCPServerBase(BaseModel):
    name: str = Field(...)
    type: Literal["http", "sse"] = Field("http")
    url: str = Field(...)
    headers: List[HeaderItem] = Field(default_factory=list)
    timeout: float = Field(30.0)
    enabled: bool = Field(True)


class MCPServerCreate(MCPServerBase):
    pass


class MCPServerUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[Literal["http", "sse"]] = None
    url: Optional[str] = None
    headers: Optional[List[HeaderItem]] = None
    timeout: Optional[float] = None
    enabled: Optional[bool] = None


class MCPToolDefinition(BaseModel):
    name: str = Field(...)
    description: Optional[str] = Field("")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    server_id: Optional[str] = Field(None)
    server_name: Optional[str] = Field(None)


class MCPServerResponse(MCPServerBase):
    id: str
    created_at: str
    updated_at: str
    tools: List[MCPToolDefinition] = Field(default_factory=list)


class PaginatedMCPServersResponse(BaseModel):
    items: List[MCPServerResponse]
    total: int
    page: int
    size: int
    pages: int


class OllamaToolFunction(BaseModel):
    name: str
    description: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)


class OllamaTool(BaseModel):
    type: Literal["function"] = "function"
    function: OllamaToolFunction


class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None

