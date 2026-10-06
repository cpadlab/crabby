import type {
    Connection,
    ConnectionCreateInput,
    ConnectionUpdateInput,
    HeaderItem,
    PaginatedConnectionsResponse,
    PyWebViewResponse,
} from "./connections"

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

export interface PyWebViewAPI {
    connections: ConnectionsPyWebViewAPI
}

declare global {
    interface Window {
        pywebview?: {
            api: PyWebViewAPI
        }
    }
}

export {}
