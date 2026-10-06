import * as React from "react"
import { useTranslation } from "react-i18next"
import { Loader2Icon, PlusIcon, RefreshCwIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useConnectionsContext } from "@/context/connections"
import { ManageConnectionForm } from "../../forms/connections/manage"
import { ConnectionCard } from "./card"
import { ConnectionsEmptyState } from "./empty"
import { ConnectionsSkeleton } from "./skeleton"
import { ConnectionsSummary } from "./summary"

export const ConnectionsSection = () => {

    const { connections, hasMore, loadMore, loading } = useConnectionsContext()
    const [createOpen, setCreateOpen] = React.useState(false)
    const { t } = useTranslation()

    const renderContent = () => {
        if (loading && connections.length === 0) {
            return <ConnectionsSkeleton />
        }

        if (connections.length > 0) {
            return (
                <div className="flex flex-col gap-4">
                    {connections.map((connection) => (
                        <ConnectionCard key={connection.id} connection={connection} />
                    ))}

                    {hasMore && (
                        <div className="flex justify-center">
                            <Button variant="outline" size="sm" onClick={loadMore} disabled={loading} className="w-full sm:w-auto">
                                {loading ? (
                                    <>
                                        <Loader2Icon className="animate-spin" />
                                        {t("connections.section.loading_more")}
                                    </>
                                ) : (
                                    <>
                                        <RefreshCwIcon />
                                        {t("connections.section.load_more")}
                                    </>
                                )}
                            </Button>
                        </div>
                    )}
                </div>
            )
        }

        return <ConnectionsEmptyState onCreateClick={() => setCreateOpen(true)} />
    }

    return (
        <section className="flex flex-col gap-4">
            
            <div className="flex items-center justify-between gap-4">
                <h2 className="text-lg font-semibold">{t("connections.section.title")}</h2>
                <ManageConnectionForm open={createOpen} onOpenChange={setCreateOpen}
                    trigger={
                        <Button size="sm" onClick={() => setCreateOpen(true)}>
                            <PlusIcon />
                            {t("connections.create.title")}
                        </Button>
                    }
                />
            </div>

            <ConnectionsSummary />

            {renderContent()}
            
        </section>
    )
}

export default ConnectionsSection
