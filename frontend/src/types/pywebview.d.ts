import type {
    Connection,
    ConnectionCreateInput,
    ConnectionUpdateInput,
    HeaderItem,
    PaginatedConnectionsResponse,
    PyWebViewResponse,
} from "./connections"
import type {
    MCPServer,
    MCPServerCreateInput,
    MCPServerUpdateInput,
    MCPToolDefinition,
    OllamaTool,
    PaginatedMCPServersResponse,
    ToolExecutionResult,
} from "./mcp"

export interface ConnectionsPyWebViewAPI {
    create(data: ConnectionCreateInput): Promise<PyWebViewResponse<Connection>>
    update(connId: string, data: ConnectionUpdateInput): Promise<PyWebViewResponse<Connection>>
    delete(connId: string): Promise<PyWebViewResponse<boolean>>
    check(connId: string): Promise<PyWebViewResponse<boolean>>
    check_by_url(host: string, headers?: HeaderItem[], timeout?: number): Promise<PyWebViewResponse<boolean>>
    get_models(connId: string): Promise<PyWebViewResponse<string[]>>
    list_paginated(
        search?: string,
        page?: number,
        size?: number,
        sort_by?: string,
        sort_order?: string
    ): Promise<PyWebViewResponse<PaginatedConnectionsResponse>>
}

export interface MCPPyWebViewAPI {
    create(data: MCPServerCreateInput): Promise<PyWebViewResponse<MCPServer>>
    update(mcpId: string, data: MCPServerUpdateInput): Promise<PyWebViewResponse<MCPServer>>
    delete(mcpId: string): Promise<PyWebViewResponse<boolean>>
    check(mcpId: string): Promise<PyWebViewResponse<boolean>>
    check_by_url(url: string, headers?: HeaderItem[], timeout?: number): Promise<PyWebViewResponse<boolean>>
    discover_tools(mcpId: string): Promise<PyWebViewResponse<MCPToolDefinition[]>>
    list_paginated(
        search?: string,
        page?: number,
        size?: number,
        sort_by?: string,
        sort_order?: string
    ): Promise<PyWebViewResponse<PaginatedMCPServersResponse>>
    get_ollama_tools(): Promise<PyWebViewResponse<OllamaTool[]>>
    execute_tool_call(tool_name: string, arguments: Record<string, unknown>): Promise<PyWebViewResponse<ToolExecutionResult>>
}

export interface PyWebViewAPI {
    connections: ConnectionsPyWebViewAPI
    mcp: MCPPyWebViewAPI
}

declare global {
    interface Window {
        pywebview?: {
            api: PyWebViewAPI
        }
    }
}

export {}
