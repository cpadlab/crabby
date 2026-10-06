import * as React from "react"
import { useTranslation } from "react-i18next"
import { PlusIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useConnectionsContext } from "@/context/connections"
import { ManageConnectionForm } from "../../forms/connections/manage"
import { ConnectionCard } from "./card"
import { ConnectionsEmptyState } from "./empty"

export const ConnectionsSection = () => {

    const { connections } = useConnectionsContext()
    const [createOpen, setCreateOpen] = React.useState(false)
    const { t } = useTranslation()

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

            {connections.length > 0 ? (
                <div className="flex flex-col gap-4">
                    {connections.map((connection) => (
                        <ConnectionCard key={connection.id} connection={connection} />
                    ))}
                </div>
            ) : (
                <ConnectionsEmptyState onCreateClick={() => setCreateOpen(true)} />
            )}
            
        </section>
    )
}

export default ConnectionsSection

