export interface HeaderItem {
    key: string
    value: string
}

export type ConnectionProviderType = "ollama"

export interface Connection {
    id: string
    name: string
    type: ConnectionProviderType
    host: string
    headers: HeaderItem[]
    timeout: number
    created_at: string
    updated_at: string
    models?: string[]
}

export interface ConnectionCreateInput {
    name: string
    type?: ConnectionProviderType
    host: string
    headers?: HeaderItem[]
    timeout?: number
}

export interface ConnectionUpdateInput {
    name?: string
    host?: string
    headers?: HeaderItem[]
    timeout?: number
}

export interface PaginatedConnectionsResponse {
    items: Connection[]
    total: number
    page: number
    size: number
    pages: number
}

export interface PyWebViewResponse<T = unknown> {
    success: boolean
    data?: T
    connected?: boolean
    error?: string
}

