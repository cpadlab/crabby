from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class HeaderItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    key: str = Field(..., min_length=1, max_length=256)
    value: str = Field("", max_length=8192)
    configured: bool = Field(False, exclude=True)

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        forbidden = {"host", "content-length", "transfer-encoding", "connection"}
        if not value.isascii() or any(not (ch.isalnum() or ch in "!#$%&'*+-.^_`|~") for ch in value):
            raise ValueError("Header name contains invalid characters.")
        if value.lower() in forbidden:
            raise ValueError("This HTTP header is managed by the client and cannot be configured.")
        return value

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: str) -> str:
        if any(ch in value for ch in "\r\n\x00"):
            raise ValueError("Header value contains invalid characters.")
        return value


def _validate_headers(headers: List[HeaderItem]) -> List[HeaderItem]:
    names = [header.key.casefold() for header in headers]
    if len(names) != len(set(names)):
        raise ValueError("Header names must be unique, ignoring case.")
    return headers


class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    type: Literal["http", "sse"] = "http"
    url: str = Field(..., min_length=1, max_length=2048)
    headers: List[HeaderItem] = Field(default_factory=list, max_length=100)
    timeout: float = Field(30.0, ge=0.5, le=300)
    enabled: bool = True

    @field_validator("name", "url")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("headers")
    @classmethod
    def unique_headers(cls, value: List[HeaderItem]) -> List[HeaderItem]:
        return _validate_headers(value)


class MCPServerCreate(MCPServerBase):
    @model_validator(mode="after")
    def require_header_values(self) -> "MCPServerCreate":
        if any(not header.value for header in self.headers):
            raise ValueError("Header values are required when creating an MCP server.")
        return self


class MCPServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    type: Optional[Literal["http", "sse"]] = None
    url: Optional[str] = Field(None, min_length=1, max_length=2048)
    headers: Optional[List[HeaderItem]] = Field(None, max_length=100)
    timeout: Optional[float] = Field(None, ge=0.5, le=300)
    enabled: Optional[bool] = None

    @field_validator("name", "url")
    @classmethod
    def trim_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("headers")
    @classmethod
    def unique_headers(cls, value: Optional[List[HeaderItem]]) -> Optional[List[HeaderItem]]:
        return _validate_headers(value) if value is not None else None


class MCPToolDefinition(BaseModel):
    name: str
    description: str = ""
    input_schema: Dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})
    parameters: Dict[str, Any] = Field(default_factory=dict)
    server_id: Optional[str] = None
    server_name: Optional[str] = None

    @model_validator(mode="after")
    def synchronize_schemas(self) -> "MCPToolDefinition":
        if not self.parameters:
            self.parameters = self.input_schema
        if not self.input_schema:
            self.input_schema = self.parameters
        return self


class MCPHeaderResponse(BaseModel):
    key: str
    value: str = ""
    configured: bool = True


class MCPServerResponse(BaseModel):
    id: str
    name: str
    type: Literal["http", "sse"]
    url: str
    headers: List[MCPHeaderResponse] = Field(default_factory=list)
    timeout: float
    enabled: bool
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
