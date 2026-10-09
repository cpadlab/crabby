import type { HeaderItem, PyWebViewResponse } from "./connections"

export type MCPServerType = "http" | "sse"
export type MCPSortOrder = "asc" | "desc"

export interface MCPHeader {
    key: string
    value: ""
    configured: boolean
}

export interface MCPServer {
    id: string
    name: string
    type: MCPServerType
    url: string
    headers: MCPHeader[]
    timeout: number
    enabled: boolean
    created_at: string
    updated_at: string
    tools?: MCPToolDefinition[]
}

export interface MCPServerCreateInput {
    name: string
    type?: MCPServerType
    url: string
    headers?: HeaderItem[]
    timeout?: number
    enabled?: boolean
}

export interface MCPServerUpdateInput {
    name?: string
    type?: MCPServerType
    url?: string
    headers?: HeaderItem[]
    timeout?: number
    enabled?: boolean
}

export interface PaginatedMCPServersResponse {
    items: MCPServer[]
    total: number
    page: number
    size: number
    pages: number
}

export interface MCPToolDefinition {
    name: string
    description: string
    input_schema: Record<string, unknown>
    parameters?: Record<string, unknown>
    server_id?: string | null
    server_name?: string | null
}

export interface OllamaToolFunction {
    name: string
    description: string
    parameters: Record<string, unknown>
}

export interface OllamaTool {
    type: "function"
    function: OllamaToolFunction
}

export interface ToolExecutionResult {
    tool_name: string
    success: boolean
    result: unknown
    error?: string | null
}

export type MCPServerResponse = PyWebViewResponse<MCPServer>
export type MCPToolListResponse = PyWebViewResponse<MCPToolDefinition[]>
export type MCPConnectionCheckResponse = PyWebViewResponse<boolean> & { connected?: boolean }
