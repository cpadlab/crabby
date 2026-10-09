import * as React from "react"
import { useTranslation } from "react-i18next"
import { Loader2Icon, PlusIcon, SearchIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useConnectionsContext } from "@/context/connections"
import { ManageConnectionForm } from "../../forms/connections/manage"
import { ConnectionCard } from "./card"
import { ConnectionsEmptyState } from "./empty"
import { ConnectionsSkeleton } from "./skeleton"
import { ConnectionsSummary } from "./summary"

export const ConnectionsSection = () => {

    const { connections, hasMore, loadMore, loading, search, setSearch, sortOrder, setSort } = useConnectionsContext()
    const [searchInput, setSearchInput] = React.useState(search)
    const [createOpen, setCreateOpen] = React.useState(false)
    const { t } = useTranslation()
    const setSearchRef = React.useRef(setSearch)
    const appliedSearch = React.useRef(search)

    React.useEffect(() => { setSearchRef.current = setSearch }, [setSearch])

    React.useEffect(() => {
        const timer = window.setTimeout(() => {
            if (searchInput !== appliedSearch.current) {
                appliedSearch.current = searchInput
                setSearchRef.current(searchInput)
            }
        }, 250)
        return () => window.clearTimeout(timer)
    }, [searchInput])

    React.useEffect(() => {
        appliedSearch.current = search
        setSearchInput(search)
    }, [search])

    return (
        <section className="flex flex-col gap-4">
            
            <header>
                <h2 className="text-xl font-semibold">{t("connections.section.title")}</h2>
                <p className="mt-1 text-sm text-muted-foreground">{t("connections.section.subtitle")}</p>
            </header>

            <ConnectionsSummary />

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                    
                    <div className="relative min-w-0 flex-1 sm:w-64 sm:flex-none">
                        <SearchIcon className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                        <Input aria-label={t("connections.section.search")} placeholder={t("connections.section.search")} value={searchInput} onChange={(event) => setSearchInput(event.target.value)} className="pl-9" />
                    </div>
                </div>
                
                <div className="flex items-center gap-2">
                    
                    <Select value={sortOrder} onValueChange={(value) => { if (value === "asc" || value === "desc") setSort("created_at", value)}}>
                        <SelectTrigger aria-label={t("connections.toolbar.sort_label")} className="w-auto sm:flex-auto flex-1">
                            <SelectValue>
                                {sortOrder === "desc"
                                    ? t("connections.toolbar.newest_first")
                                    : t("connections.toolbar.oldest_first")}
                            </SelectValue>
                        </SelectTrigger>
                        <SelectContent align="end">
                            <SelectItem value="desc">{t("connections.toolbar.newest_first")}</SelectItem>
                            <SelectItem value="asc">{t("connections.toolbar.oldest_first")}</SelectItem>
                        </SelectContent>
                    </Select>

                    <ManageConnectionForm open={createOpen} onOpenChange={setCreateOpen} 
                        trigger={
                            <Button className="sm:flex-auto flex-1" onClick={() => setCreateOpen(true)}>
                                <PlusIcon />
                                <span>{t("connections.create.title")}</span>
                            </Button>} 
                        />

                </div>

            </div>

            {loading && connections.length === 0 ? <ConnectionsSkeleton /> : connections.length ? (
                <div className="space-y-3">
                    {connections.map((connection) => <ConnectionCard key={connection.id} connection={connection} />)}
                    {hasMore && <div className="flex justify-center pt-2"><Button variant="outline" size="sm" onClick={loadMore} disabled={loading}>{loading && <Loader2Icon className="animate-spin" />}{t(loading ? "connections.section.loading_more" : "connections.section.load_more")}</Button></div>}
                </div>
            ) : searchInput ? (
                <div className="rounded-xl border border-dashed py-12 text-center text-sm text-muted-foreground">{t("connections.section.no_search_results", { search: searchInput })}</div>
            ) : <ConnectionsEmptyState onCreateClick={() => setCreateOpen(true)} />}

        </section>
    )
}

export default ConnectionsSection
