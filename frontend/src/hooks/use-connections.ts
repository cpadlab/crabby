import * as React from "react"
import { useTranslation } from "react-i18next"

import { toast } from "@/components/ui/toast"
import type {
    Connection,
    ConnectionCreateInput,
    ConnectionUpdateInput,
    HeaderItem,
    PaginatedConnectionsResponse,
    PyWebViewResponse,
} from "@/types/connections"

export interface UseConnectionsReturn {
    connections: Connection[]
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
    loadConnections: (overrideParams?: {
        search?: string
        page?: number
        size?: number
        sortBy?: string
        sortOrder?: "asc" | "desc"
        append?: boolean
    }) => Promise<void>
    loadMore: () => Promise<void>
    createConnection: (input: ConnectionCreateInput) => Promise<PyWebViewResponse<Connection>>
    updateConnection: (id: string, input: ConnectionUpdateInput) => Promise<PyWebViewResponse<Connection>>
    deleteConnection: (id: string) => Promise<PyWebViewResponse<boolean>>
    checkConnection: (id: string) => Promise<boolean>
    checkConnectionByUrl: (host: string, headers?: HeaderItem[], timeout?: number) => Promise<boolean>
    getModels: (id: string) => Promise<string[]>
    setSearch: (term: string) => void
    setPage: (newPage: number) => void
    setSort: (newSortBy: string, newSortOrder?: "asc" | "desc") => void
}

export function useConnections(): UseConnectionsReturn {
    const { t } = useTranslation()
    const [connections, setConnections] = React.useState<Connection[]>([])
    const [total, setTotal] = React.useState(0)
    const [page, setPage] = React.useState(1)
    const [size, setSize] = React.useState(10)
    const [pages, setPages] = React.useState(0)
    const [loading, setLoading] = React.useState(false)
    const [error, setError] = React.useState<string | null>(null)
    const [search, setSearchState] = React.useState("")
    const [sortBy, setSortByState] = React.useState("created_at")
    const [sortOrder, setSortOrderState] = React.useState<"asc" | "desc">("desc")

    const loadConnections = React.useCallback(
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
                if (window.pywebview?.api?.connections) {
                    const res = await window.pywebview.api.connections.list_paginated(
                        currentSearch,
                        currentPage,
                        currentSize,
                        currentSortBy,
                        currentSortOrder
                    )

                    if (res.success && res.data) {
                        const data: PaginatedConnectionsResponse = res.data
                        if (isAppend) {
                            setConnections((prev) => {
                                const existingIds = new Set(prev.map((item) => item.id))
                                const newItems = data.items.filter((item) => !existingIds.has(item.id))
                                return [...prev, ...newItems]
                            })
                        } else {
                            setConnections(data.items)
                        }
                        setTotal(data.total)
                        setPage(data.page)
                        setSize(data.size)
                        setPages(data.pages)
                    } else {
                        const errorMsg = res.error || t("connections.errors.load_failed")
                        setError(errorMsg)
                        toast.add({
                            type: "error",
                            title: t("connections.errors.title"),
                            description: errorMsg,
                        })
                    }
                } else {
                    if (!isAppend) setConnections([])
                    setTotal(0)
                    setPages(0)
                }
            } catch (err) {
                const errorMsg = err instanceof Error ? err.message : t("connections.errors.unexpected_error")
                setError(errorMsg)
                toast.add({
                    type: "error",
                    title: t("connections.errors.title"),
                    description: errorMsg,
                })
            } finally {
                setLoading(false)
            }
        },
        [search, page, size, sortBy, sortOrder, t]
    )

    React.useEffect(() => {
        loadConnections({ page: 1 })

        const handlePyWebViewReady = () => {
            loadConnections({ page: 1 })
        }

        window.addEventListener("pywebviewready", handlePyWebViewReady)
        return () => {
            window.removeEventListener("pywebviewready", handlePyWebViewReady)
        }
    }, [])

    const loadMore = React.useCallback(async () => {
        if (loading || page >= pages) return
        await loadConnections({ page: page + 1, append: true })
    }, [loading, page, pages, loadConnections])

    const createConnection = React.useCallback(
        async (input: ConnectionCreateInput): Promise<PyWebViewResponse<Connection>> => {
            if (!window.pywebview?.api?.connections) {
                const errorMsg = t("connections.errors.pywebview_not_available")
                toast.add({
                    type: "error",
                    title: t("connections.errors.title"),
                    description: errorMsg,
                })
                return { success: false, error: errorMsg }
            }

            const res = await window.pywebview.api.connections.create(input)
            if (res.success) {
                toast.add({
                    type: "success",
                    title: t("connections.success.title"),
                    description: t("connections.success.create_success"),
                })
                await loadConnections()
            } else {
                const errorMsg = res.error || t("connections.errors.create_failed")
                toast.add({
                    type: "error",
                    title: t("connections.errors.title"),
                    description: errorMsg,
                })
            }
            return res
        },
        [loadConnections, t]
    )

    const updateConnection = React.useCallback(
        async (id: string, input: ConnectionUpdateInput): Promise<PyWebViewResponse<Connection>> => {
            if (!window.pywebview?.api?.connections) {
                const errorMsg = t("connections.errors.pywebview_not_available")
                toast.add({
                    type: "error",
                    title: t("connections.errors.title"),
                    description: errorMsg,
                })
                return { success: false, error: errorMsg }
            }

            const res = await window.pywebview.api.connections.update(id, input)
            if (res.success) {
                toast.add({
                    type: "success",
                    title: t("connections.success.title"),
                    description: t("connections.success.update_success"),
                })
                await loadConnections()
            } else {
                const errorMsg = res.error || t("connections.errors.update_failed")
                toast.add({
                    type: "error",
                    title: t("connections.errors.title"),
                    description: errorMsg,
                })
            }
            return res
        },
        [loadConnections, t]
    )

    const deleteConnection = React.useCallback(
        async (id: string): Promise<PyWebViewResponse<boolean>> => {
            if (!window.pywebview?.api?.connections) {
                const errorMsg = t("connections.errors.pywebview_not_available")
                toast.add({
                    type: "error",
                    title: t("connections.errors.title"),
                    description: errorMsg,
                })
                return { success: false, error: errorMsg }
            }

            const res = await window.pywebview.api.connections.delete(id)
            if (res.success) {
                toast.add({
                    type: "success",
                    title: t("connections.success.title"),
                    description: t("connections.success.delete_success"),
                })
                await loadConnections()
            } else {
                const errorMsg = res.error || t("connections.errors.delete_failed")
                toast.add({
                    type: "error",
                    title: t("connections.errors.title"),
                    description: errorMsg,
                })
            }
            return res
        },
        [loadConnections, t]
    )

    const checkConnection = React.useCallback(async (id: string): Promise<boolean> => {
        if (!window.pywebview?.api?.connections) return false
        const res = await window.pywebview.api.connections.check(id)
        return Boolean(res.success && res.connected)
    }, [])

    const checkConnectionByUrl = React.useCallback(
        async (host: string, headers?: HeaderItem[], timeout?: number): Promise<boolean> => {
            if (!window.pywebview?.api?.connections) return false
            const res = await window.pywebview.api.connections.check_by_url(host, headers, timeout)
            return Boolean(res.success && res.connected)
        },
        []
    )

    const getModels = React.useCallback(async (id: string): Promise<string[]> => {
        if (!window.pywebview?.api?.connections) return []
        const res = await window.pywebview.api.connections.get_models(id)
        return res.success && res.data ? res.data : []
    }, [])

    const setSearch = React.useCallback(
        (term: string) => {
            setSearchState(term)
            setPage(1)
            loadConnections({ search: term, page: 1 })
        },
        [loadConnections]
    )

    const handleSetPage = React.useCallback(
        (newPage: number) => {
            setPage(newPage)
            loadConnections({ page: newPage })
        },
        [loadConnections]
    )

    const setSort = React.useCallback(
        (newSortBy: string, newSortOrder?: "asc" | "desc") => {
            const order = newSortOrder ?? (sortBy === newSortBy && sortOrder === "desc" ? "asc" : "desc")
            setSortByState(newSortBy)
            setSortOrderState(order)
            loadConnections({ sortBy: newSortBy, sortOrder: order })
        },
        [sortBy, sortOrder, loadConnections]
    )

    return {
        connections,
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
        loadConnections,
        loadMore,
        createConnection,
        updateConnection,
        deleteConnection,
        checkConnection,
        checkConnectionByUrl,
        getModels,
        setSearch,
        setPage: handleSetPage,
        setSort,
    }
}

export default useConnections
