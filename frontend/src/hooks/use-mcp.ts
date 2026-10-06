import * as React from "react"
import { useTranslation } from "react-i18next"

import { toast } from "@/components/ui/toast"
import type { HeaderItem, PyWebViewResponse } from "@/types/connections"
import type { MCPServer, MCPServerCreateInput, MCPServerUpdateInput, MCPToolDefinition, OllamaTool, PaginatedMCPServersResponse, ToolExecutionResult } from "@/types/mcp"

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
    loadMCPServers: (overrideParams?: {
        search?: string
        page?: number
        size?: number
        sortBy?: string
        sortOrder?: "asc" | "desc"
        append?: boolean
    }) => Promise<void>
    loadMore: () => Promise<void>
    createMCPServer: (input: MCPServerCreateInput) => Promise<PyWebViewResponse<MCPServer>>
    updateMCPServer: (id: string, input: MCPServerUpdateInput) => Promise<PyWebViewResponse<MCPServer>>
    deleteMCPServer: (id: string) => Promise<PyWebViewResponse<boolean>>
    checkMCPServer: (id: string) => Promise<boolean>
    checkMCPServerByUrl: (url: string, headers?: HeaderItem[], timeout?: number) => Promise<boolean>
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
    const [page, setPage] = React.useState(1)
    const [size, setSize] = React.useState(10)
    const [pages, setPages] = React.useState(0)
    const [loading, setLoading] = React.useState(false)
    const [error, setError] = React.useState<string | null>(null)
    const [search, setSearchState] = React.useState("")
    const [sortBy, setSortByState] = React.useState("created_at")
    const [sortOrder, setSortOrderState] = React.useState<"asc" | "desc">("desc")

    const loadMCPServers = React.useCallback(
        async (overrideParams?: {
            search?: string
            page?: number
            size?: number
            sortBy?: string
            sortOrder?: "asc" | "desc"
            append?: boolean
        }) => {
            setLoading(true)
            setError(null)

            const currentSearch = overrideParams?.search ?? search
            const currentPage = overrideParams?.page ?? page
            const currentSize = overrideParams?.size ?? size
            const currentSortBy = overrideParams?.sortBy ?? sortBy
            const currentSortOrder = overrideParams?.sortOrder ?? sortOrder
            const isAppend = overrideParams?.append ?? false

            try {
                if (window.pywebview?.api?.mcp) {
                    const res = await window.pywebview.api.mcp.list_paginated(
                        currentSearch,
                        currentPage,
                        currentSize,
                        currentSortBy,
                        currentSortOrder
                    )

                    if (res.success && res.data) {
                        const data: PaginatedMCPServersResponse = res.data
                        if (isAppend) {
                            setMcpServers((prev) => {
                                const existingIds = new Set(prev.map((item) => item.id))
                                const newItems = data.items.filter((item) => !existingIds.has(item.id))
                                return [...prev, ...newItems]
                            })
                        } else {
                            setMcpServers(data.items)
                        }
                        setTotal(data.total)
                        setPage(data.page)
                        setSize(data.size)
                        setPages(data.pages)
                    } else {
                        const errorMsg = res.error || t("mcp.errors.load_failed", "Error al cargar servidores MCP")
                        setError(errorMsg)
                        toast.add({
                            type: "error",
                            title: t("mcp.errors.title", "Error"),
                            description: errorMsg,
                        })
                    }
                } else {
                    if (!isAppend) setMcpServers([])
                    setTotal(0)
                    setPages(0)
                }
            } catch (err) {
                const errorMsg = err instanceof Error ? err.message : t("mcp.errors.unexpected_error", "Error inesperado")
                setError(errorMsg)
                toast.add({
                    type: "error",
                    title: t("mcp.errors.title", "Error"),
                    description: errorMsg,
                })
            } finally {
                setLoading(false)
            }
        },
        [search, page, size, sortBy, sortOrder, t]
    )

    React.useEffect(() => {
        loadMCPServers({ page: 1 })

        const handlePyWebViewReady = () => {
            loadMCPServers({ page: 1 })
        }

        window.addEventListener("pywebviewready", handlePyWebViewReady)
        return () => {
            window.removeEventListener("pywebviewready", handlePyWebViewReady)
        }
    }, [])

    const loadMore = React.useCallback(async () => {
        if (loading || page >= pages) return
        await loadMCPServers({ page: page + 1, append: true })
    }, [loading, page, pages, loadMCPServers])

    const createMCPServer = React.useCallback(
        async (input: MCPServerCreateInput): Promise<PyWebViewResponse<MCPServer>> => {
            if (!window.pywebview?.api?.mcp) {
                const errorMsg = t("mcp.errors.pywebview_not_available", "API backend no disponible")
                toast.add({
                    type: "error",
                    title: t("mcp.errors.title", "Error"),
                    description: errorMsg,
                })
                return { success: false, error: errorMsg }
            }

            const res = await window.pywebview.api.mcp.create(input)
            if (res.success) {
                toast.add({
                    type: "success",
                    title: t("mcp.success.title", "Éxito"),
                    description: t("mcp.success.create_success", "Servidor MCP creado correctamente"),
                })
                await loadMCPServers()
            } else {
                const errorMsg = res.error || t("mcp.errors.create_failed", "Error al crear servidor MCP")
                toast.add({
                    type: "error",
                    title: t("mcp.errors.title", "Error"),
                    description: errorMsg,
                })
            }
            return res
        },
        [loadMCPServers, t]
    )

    const updateMCPServer = React.useCallback(
        async (id: string, input: MCPServerUpdateInput): Promise<PyWebViewResponse<MCPServer>> => {
            if (!window.pywebview?.api?.mcp) {
                const errorMsg = t("mcp.errors.pywebview_not_available", "API backend no disponible")
                toast.add({
                    type: "error",
                    title: t("mcp.errors.title", "Error"),
                    description: errorMsg,
                })
                return { success: false, error: errorMsg }
            }

            const res = await window.pywebview.api.mcp.update(id, input)
            if (res.success) {
                toast.add({
                    type: "success",
                    title: t("mcp.success.title", "Éxito"),
                    description: t("mcp.success.update_success", "Servidor MCP actualizado correctamente"),
                })
                await loadMCPServers()
            } else {
                const errorMsg = res.error || t("mcp.errors.update_failed", "Error al actualizar servidor MCP")
                toast.add({
                    type: "error",
                    title: t("mcp.errors.title", "Error"),
                    description: errorMsg,
                })
            }
            return res
        },
        [loadMCPServers, t]
    )

    const deleteMCPServer = React.useCallback(
        async (id: string): Promise<PyWebViewResponse<boolean>> => {
            if (!window.pywebview?.api?.mcp) {
                const errorMsg = t("mcp.errors.pywebview_not_available", "API backend no disponible")
                toast.add({
                    type: "error",
                    title: t("mcp.errors.title", "Error"),
                    description: errorMsg,
                })
                return { success: false, error: errorMsg }
            }

            const res = await window.pywebview.api.mcp.delete(id)
            if (res.success) {
                toast.add({
                    type: "success",
                    title: t("mcp.success.title", "Éxito"),
                    description: t("mcp.success.delete_success", "Servidor MCP eliminado correctamente"),
                })
                await loadMCPServers()
            } else {
                const errorMsg = res.error || t("mcp.errors.delete_failed", "Error al eliminar servidor MCP")
                toast.add({
                    type: "error",
                    title: t("mcp.errors.title", "Error"),
                    description: errorMsg,
                })
            }
            return res
        },
        [loadMCPServers, t]
    )

    const checkMCPServer = React.useCallback(async (id: string): Promise<boolean> => {
        if (!window.pywebview?.api?.mcp) return false
        const res = await window.pywebview.api.mcp.check(id)
        return Boolean(res.success && res.connected)
    }, [])

    const checkMCPServerByUrl = React.useCallback(
        async (url: string, headers?: HeaderItem[], timeout?: number): Promise<boolean> => {
            if (!window.pywebview?.api?.mcp) return false
            const res = await window.pywebview.api.mcp.check_by_url(url, headers, timeout)
            return Boolean(res.success && res.connected)
        },
        []
    )

    const discoverTools = React.useCallback(async (id: string): Promise<MCPToolDefinition[]> => {
        if (!window.pywebview?.api?.mcp) return []
        const res = await window.pywebview.api.mcp.discover_tools(id)
        return res.success && res.data ? res.data : []
    }, [])

    const getOllamaTools = React.useCallback(async (): Promise<OllamaTool[]> => {
        if (!window.pywebview?.api?.mcp) return []
        const res = await window.pywebview.api.mcp.get_ollama_tools()
        return res.success && res.data ? res.data : []
    }, [])

    const executeToolCall = React.useCallback(
        async (toolName: string, args: Record<string, unknown>): Promise<PyWebViewResponse<ToolExecutionResult>> => {
            if (!window.pywebview?.api?.mcp) {
                return { success: false, error: "PyWebView API not available" }
            }
            return await window.pywebview.api.mcp.execute_tool_call(toolName, args)
        },
        []
    )

    const setSearch = React.useCallback(
        (term: string) => {
            setSearchState(term)
            setPage(1)
            loadMCPServers({ search: term, page: 1 })
        },
        [loadMCPServers]
    )

    const handleSetPage = React.useCallback(
        (newPage: number) => {
            setPage(newPage)
            loadMCPServers({ page: newPage })
        },
        [loadMCPServers]
    )

    const setSort = React.useCallback(
        (newSortBy: string, newSortOrder?: "asc" | "desc") => {
            const order = newSortOrder ?? (sortBy === newSortBy && sortOrder === "desc" ? "asc" : "desc")
            setSortByState(newSortBy)
            setSortOrderState(order)
            loadMCPServers({ sortBy: newSortBy, sortOrder: order })
        },
        [sortBy, sortOrder, loadMCPServers]
    )

    return {
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
        checkMCPServerByUrl,
        discoverTools,
        getOllamaTools,
        executeToolCall,
        setSearch,
        setPage: handleSetPage,
        setSort,
    }
}

export default useMCP

