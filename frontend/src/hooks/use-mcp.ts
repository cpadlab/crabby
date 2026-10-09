import * as React from "react"
import { useTranslation } from "react-i18next"

import { toast } from "@/components/ui/toast"
import type { HeaderItem, PyWebViewResponse } from "@/types/connections"
import type {
    MCPConnectionCheckResponse,
    MCPServer,
    MCPServerCreateInput,
    MCPServerType,
    MCPServerUpdateInput,
    MCPToolDefinition,
    OllamaTool,
    ToolExecutionResult,
} from "@/types/mcp"

export interface MCPListOptions {
    search?: string
    page?: number
    size?: number
    sortBy?: string
    sortOrder?: "asc" | "desc"
    append?: boolean
}

export interface UseMCPReturn {
    mcpServers: MCPServer[]
    total: number
    page: number
    size: number
    pages: number
    loading: boolean
    hasMore: boolean
    error: string | null
    search: string
    sortBy: string
    sortOrder: "asc" | "desc"
    loadMCPServers: (overrideParams?: MCPListOptions) => Promise<void>
    loadMore: () => Promise<void>
    createMCPServer: (input: MCPServerCreateInput) => Promise<PyWebViewResponse<MCPServer>>
    updateMCPServer: (id: string, input: MCPServerUpdateInput) => Promise<PyWebViewResponse<MCPServer>>
    deleteMCPServer: (id: string) => Promise<PyWebViewResponse<boolean>>
    checkMCPServer: (id: string) => Promise<boolean>
    checkMCPServerResult: (id: string) => Promise<MCPConnectionCheckResponse>
    checkMCPServerByUrl: (
        url: string,
        headers?: HeaderItem[],
        timeout?: number,
        transportType?: MCPServerType,
    ) => Promise<boolean>
    checkMCPServerByUrlResult: (
        url: string,
        headers?: HeaderItem[],
        timeout?: number,
        transportType?: MCPServerType,
    ) => Promise<MCPConnectionCheckResponse>
    discoverTools: (id: string) => Promise<MCPToolDefinition[]>
    getOllamaTools: () => Promise<OllamaTool[]>
    executeToolCall: (toolName: string, args: Record<string, unknown>) => Promise<PyWebViewResponse<ToolExecutionResult>>
    setSearch: (term: string) => void
    setPage: (newPage: number) => void
    setSort: (newSortBy: string, newSortOrder?: "asc" | "desc") => void
}

export function useMCP(): UseMCPReturn {
    const { t } = useTranslation()
    const [mcpServers, setMcpServers] = React.useState<MCPServer[]>([])
    const [total, setTotal] = React.useState(0)
    const [page, setPageState] = React.useState(1)
    const [size, setSize] = React.useState(10)
    const [pages, setPages] = React.useState(0)
    const [loading, setLoading] = React.useState(false)
    const [error, setError] = React.useState<string | null>(null)
    const [search, setSearchState] = React.useState("")
    const [sortBy, setSortByState] = React.useState("created_at")
    const [sortOrder, setSortOrderState] = React.useState<"asc" | "desc">("desc")
    const requestSequence = React.useRef(0)
    const loadMCPServersRef = React.useRef<(options?: MCPListOptions) => Promise<void>>(async () => undefined)

    const loadMCPServers = React.useCallback(async (overrideParams?: MCPListOptions) => {
        const requestId = ++requestSequence.current
        const currentSearch = overrideParams?.search ?? search
        const currentPage = Math.max(1, overrideParams?.page ?? page)
        const currentSize = Math.max(1, Math.min(100, overrideParams?.size ?? size))
        const currentSortBy = overrideParams?.sortBy ?? sortBy
        const currentSortOrder = overrideParams?.sortOrder ?? sortOrder
        const append = overrideParams?.append ?? false
        const api = window.pywebview?.api?.mcp

        if (!api) {
            if (!append) {
                setMcpServers([])
                setTotal(0)
                setPageState(1)
                setPages(0)
            }
            setLoading(false)
            return
        }

        setLoading(true)
        setError(null)
        try {
            const response = await api.list_paginated(
                currentSearch,
                currentPage,
                currentSize,
                currentSortBy,
                currentSortOrder,
            )
            if (requestId !== requestSequence.current) return

            if (!response.success || !response.data) {
                throw new Error(response.error || t("mcp.errors.load_failed", "Error al cargar servidores MCP"))
            }

            const data = response.data
            if (append) {
                setMcpServers((previous) => {
                    const merged = new Map(previous.map((server) => [server.id, server]))
                    for (const server of data.items) merged.set(server.id, server)
                    return [...merged.values()]
                })
            } else {
                setMcpServers(data.items)
            }
            setTotal(data.total)
            setPageState(data.page)
            setSize(data.size)
            setPages(data.pages)
        } catch (cause) {
            if (requestId !== requestSequence.current) return
            const message = cause instanceof Error
                ? cause.message
                : t("mcp.errors.unexpected_error", "Error inesperado")
            setError(message)
            toast.add({
                type: "error",
                title: t("mcp.errors.title", "Error"),
                description: message,
            })
        } finally {
            if (requestId === requestSequence.current) setLoading(false)
        }
    }, [page, search, size, sortBy, sortOrder, t])

    React.useEffect(() => {
        loadMCPServersRef.current = loadMCPServers
    }, [loadMCPServers])

    React.useEffect(() => {
        void loadMCPServersRef.current({ page: 1 })
        const onReady = () => void loadMCPServersRef.current({ page: 1 })
        window.addEventListener("pywebviewready", onReady)
        return () => {
            requestSequence.current += 1
            window.removeEventListener("pywebviewready", onReady)
        }
    }, []) // Load once on mount; PyWebView may become available afterward.

    const loadMore = React.useCallback(async () => {
        if (loading || page >= pages) return
        await loadMCPServers({ page: page + 1, append: true })
    }, [loading, page, pages, loadMCPServers])

    const mutationError = React.useCallback((key: string) => t(key, "No se pudo completar la operación."), [t])

    const createMCPServer = React.useCallback(async (input: MCPServerCreateInput) => {
        const api = window.pywebview?.api?.mcp
        if (!api) return { success: false, error: t("mcp.errors.pywebview_not_available", "API backend no disponible") }
        let response: PyWebViewResponse<MCPServer>
        try {
            response = await api.create(input)
        } catch {
            response = { success: false, error: mutationError("mcp.errors.unexpected_error") }
        }
        if (response.success) {
            toast.add({ type: "success", title: t("mcp.success.title", "Éxito"), description: t("mcp.success.create_success", "Servidor MCP creado correctamente") })
            await loadMCPServers({ page: 1 })
        } else {
            toast.add({ type: "error", title: t("mcp.errors.title", "Error"), description: response.error || mutationError("mcp.errors.create_failed") })
        }
        return response
    }, [loadMCPServers, mutationError, t])

    const updateMCPServer = React.useCallback(async (id: string, input: MCPServerUpdateInput) => {
        const api = window.pywebview?.api?.mcp
        if (!api) return { success: false, error: t("mcp.errors.pywebview_not_available", "API backend no disponible") }
        let response: PyWebViewResponse<MCPServer>
        try {
            response = await api.update(id, input)
        } catch {
            response = { success: false, error: mutationError("mcp.errors.unexpected_error") }
        }
        if (response.success) {
            toast.add({ type: "success", title: t("mcp.success.title", "Éxito"), description: t("mcp.success.update_success", "Servidor MCP actualizado correctamente") })
            await loadMCPServers({ page: 1 })
        } else {
            toast.add({ type: "error", title: t("mcp.errors.title", "Error"), description: response.error || mutationError("mcp.errors.update_failed") })
        }
        return response
    }, [loadMCPServers, mutationError, t])

    const deleteMCPServer = React.useCallback(async (id: string) => {
        const api = window.pywebview?.api?.mcp
        if (!api) return { success: false, error: t("mcp.errors.pywebview_not_available", "API backend no disponible") }
        let response: PyWebViewResponse<boolean>
        try {
            response = await api.delete(id)
        } catch {
            response = { success: false, error: mutationError("mcp.errors.unexpected_error") }
        }
        if (response.success) {
            toast.add({ type: "success", title: t("mcp.success.title", "Éxito"), description: t("mcp.success.delete_success", "Servidor MCP eliminado correctamente") })
            await loadMCPServers({ page: 1 })
        } else {
            toast.add({ type: "error", title: t("mcp.errors.title", "Error"), description: response.error || mutationError("mcp.errors.delete_failed") })
        }
        return response
    }, [loadMCPServers, mutationError, t])

    const checkMCPServerResult = React.useCallback(async (id: string): Promise<MCPConnectionCheckResponse> => {
        const api = window.pywebview?.api?.mcp
        if (!api) return { success: false, connected: false, error: t("mcp.errors.pywebview_not_available", "API backend no disponible") }
        try {
            return await api.check(id)
        } catch {
            return { success: false, connected: false, error: mutationError("mcp.errors.unexpected_error") }
        }
    }, [mutationError, t])

    const checkMCPServer = React.useCallback(async (id: string) => {
        const result = await checkMCPServerResult(id)
        return Boolean(result.success && result.connected)
    }, [checkMCPServerResult])

    const checkMCPServerByUrlResult = React.useCallback(async (
        url: string,
        headers: HeaderItem[] = [],
        timeout = 5,
        transportType: MCPServerType = "http",
    ): Promise<MCPConnectionCheckResponse> => {
        const api = window.pywebview?.api?.mcp
        if (!api) {
            return { success: false, connected: false, error: t("mcp.errors.pywebview_not_available", "API backend no disponible") }
        }
        try {
            // The 4th argument selects HTTP/SSE; older bridge declarations only describe the first 3.
            const checkByUrl = api.check_by_url as (
                url: string,
                headers?: HeaderItem[],
                timeout?: number,
                transportType?: MCPServerType,
            ) => Promise<MCPConnectionCheckResponse>
            return await checkByUrl.call(api, url, headers, timeout, transportType)
        } catch {
            return { success: false, connected: false, error: mutationError("mcp.errors.unexpected_error") }
        }
    }, [mutationError, t])

    const checkMCPServerByUrl = React.useCallback(async (
        url: string,
        headers?: HeaderItem[],
        timeout?: number,
        transportType?: MCPServerType,
    ) => {
        const result = await checkMCPServerByUrlResult(url, headers, timeout, transportType)
        return Boolean(result.success && result.connected)
    }, [checkMCPServerByUrlResult])

    const discoverTools = React.useCallback(async (id: string): Promise<MCPToolDefinition[]> => {
        const api = window.pywebview?.api?.mcp
        if (!api) throw new Error(t("mcp.errors.pywebview_not_available", "API backend no disponible"))
        const response = await api.discover_tools(id)
        if (!response.success) throw new Error(response.error || mutationError("mcp.errors.discover_failed"))
        return response.data || []
    }, [mutationError, t])

    const getOllamaTools = React.useCallback(async (): Promise<OllamaTool[]> => {
        const api = window.pywebview?.api?.mcp
        if (!api) throw new Error(t("mcp.errors.pywebview_not_available", "API backend no disponible"))
        const response = await api.get_ollama_tools()
        if (!response.success) throw new Error(response.error || mutationError("mcp.errors.tools_failed"))
        return response.data || []
    }, [mutationError, t])

    const executeToolCall = React.useCallback(async (
        toolName: string,
        args: Record<string, unknown>,
    ): Promise<PyWebViewResponse<ToolExecutionResult>> => {
        const api = window.pywebview?.api?.mcp
        if (!api) return { success: false, error: t("mcp.errors.pywebview_not_available", "API backend no disponible") }
        try {
            return await api.execute_tool_call(toolName, args)
        } catch {
            return { success: false, error: mutationError("mcp.errors.unexpected_error") }
        }
    }, [mutationError, t])

    const setSearch = React.useCallback((term: string) => {
        setSearchState(term)
        setPageState(1)
        void loadMCPServers({ search: term, page: 1 })
    }, [loadMCPServers])

    const setPage = React.useCallback((newPage: number) => {
        const nextPage = Math.max(1, Math.min(newPage, Math.max(pages, 1)))
        setPageState(nextPage)
        void loadMCPServers({ page: nextPage })
    }, [loadMCPServers, pages])

    const setSort = React.useCallback((newSortBy: string, newSortOrder?: "asc" | "desc") => {
        const nextOrder = newSortOrder ?? (sortBy === newSortBy && sortOrder === "desc" ? "asc" : "desc")
        setSortByState(newSortBy)
        setSortOrderState(nextOrder)
        setPageState(1)
        void loadMCPServers({ page: 1, sortBy: newSortBy, sortOrder: nextOrder })
    }, [loadMCPServers, sortBy, sortOrder])

    return React.useMemo(() => ({
        mcpServers,
        total,
        page,
        size,
        pages,
        loading,
        hasMore: page < pages,
        error,
        search,
        sortBy,
        sortOrder,
        loadMCPServers,
        loadMore,
        createMCPServer,
        updateMCPServer,
        deleteMCPServer,
        checkMCPServer,
        checkMCPServerResult,
        checkMCPServerByUrl,
        checkMCPServerByUrlResult,
        discoverTools,
        getOllamaTools,
        executeToolCall,
        setSearch,
        setPage,
        setSort,
    }), [
        mcpServers, total, page, size, pages, loading, error, search, sortBy, sortOrder,
        loadMCPServers, loadMore, createMCPServer, updateMCPServer, deleteMCPServer,
        checkMCPServer, checkMCPServerResult, checkMCPServerByUrl, checkMCPServerByUrlResult,
        discoverTools, getOllamaTools, executeToolCall, setSearch, setPage, setSort,
    ])
}

export default useMCP
