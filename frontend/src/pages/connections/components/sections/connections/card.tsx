import * as React from "react"
import { useTranslation } from "react-i18next"
import { ActivityIcon, MoreVerticalIcon, PencilIcon, RefreshCcwIcon, RefreshCwIcon, Trash2Icon } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { toast } from "@/components/ui/toast"
import { useConnectionsContext } from "@/context/connections"
import type { Connection } from "@/types/connections"
import { DeleteConnectionDialog } from "../../forms/connections/delete"
import { ManageConnectionForm } from "../../forms/connections/manage"

export interface ConnectionCardProps {
    connection: Connection
}

export function ConnectionCard({ connection }: ConnectionCardProps) {

    const { t } = useTranslation()
    const { checkConnection, getModels } = useConnectionsContext()

    const [editOpen, setEditOpen] = React.useState(false)
    const [deleteOpen, setDeleteOpen] = React.useState(false)

    const [isConnected, setIsConnected] = React.useState<boolean | null>(null)
    const [isChecking, setIsChecking] = React.useState(false)
    const [isSyncing, setIsSyncing] = React.useState(false)
    const [models, setModels] = React.useState<string[]>(connection.models || [])

    React.useEffect(() => {
        let isMounted = true
        checkConnection(connection.id).then((ok) => {
            if (isMounted) setIsConnected(ok)
        })
        return () => {
            isMounted = false
        }
    }, [connection.id, checkConnection])

    const handleTestConnection = async () => {
        setIsChecking(true)
        try {
            const ok = await checkConnection(connection.id)
            setIsConnected(ok)
            if (ok) {
                toast.add({
                    type: "success",
                    title: connection.name,
                    description: t("connections.card.connection_ok"),
                })
            } else {
                toast.add({
                    type: "error",
                    title: connection.name,
                    description: t("connections.card.connection_failed"),
                })
            }
        } catch {
            setIsConnected(false)
            toast.add({
                type: "error",
                title: connection.name,
                description: t("connections.errors.unexpected_error"),
            })
        } finally {
            setIsChecking(false)
        }
    }

    const handleSyncModels = async () => {
        setIsSyncing(true)
        try {
            const fetched = await getModels(connection.id)
            setModels(fetched)
            toast.add({
                type: "success",
                title: connection.name,
                description: t("connections.card.models_synced", { count: fetched.length }),
            })
        } catch {
            toast.add({
                type: "error",
                title: connection.name,
                description: t("connections.errors.unexpected_error"),
            })
        } finally {
            setIsSyncing(false)
        }
    }

    const initials = (connection.name || "ON").slice(0, 2).toUpperCase()
    const headerCount = connection.headers?.length || 0

    const displayedModels = models.slice(0, 2)
    const extraModelsCount = models.length > 2 ? models.length - 2 : 0

    return (
        <>
            <div className="bg-card overflow-hidden border rounded-xl transition-colors hover:border-border/80">
                
                <div className="flex p-4 items-start sm:items-center justify-between gap-3 sm:gap-4">
                    
                    <div className="flex items-start sm:items-center gap-3 min-w-0 flex-1">
                        <div className="p-2.5 bg-primary text-primary-foreground font-bold rounded-2xl shrink-0 text-sm flex items-center justify-center min-w-[38px] h-[38px] mt-0.5 sm:mt-0">
                            <span>{initials}</span>
                        </div>
                        <div className="flex flex-col gap-1.5 min-w-0 flex-1">
                            <p className="text-base sm:text-lg leading-none font-medium truncate">{connection.name}</p>
                            <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs sm:text-sm">
                                <Badge variant="outline" className="gap-1.5 max-w-full">
                                    <div className={`w-2 h-2 rounded-full shrink-0 ${isConnected === true ? "bg-emerald-500" : isConnected === false ? "bg-destructive" : "bg-amber-500"}`} />
                                    <span className="truncate max-w-[160px] sm:max-w-xs">{connection.host}</span>
                                </Badge>
                                <span className="md:inline hidden text-muted-foreground">• {t("connections.card.timeout", { timeout: connection.timeout })}</span>
                                <span className="md:inline hidden text-muted-foreground">• {t(headerCount === 1 ? "connections.card.headers_count_one" : "connections.card.headers_count_other", { count: headerCount })}</span>
                            </div>
                        </div>
                    </div>

                    <DropdownMenu>

                        <DropdownMenuTrigger
                            render={
                                <Button size="icon-sm" variant="ghost" className="shrink-0 -mt-1 sm:mt-0">
                                    <MoreVerticalIcon className="w-4 h-4" />
                                </Button>
                            }
                        />

                        <DropdownMenuContent className="w-auto" align="end">
                            <DropdownMenuItem onClick={handleTestConnection} disabled={isChecking}>
                                <ActivityIcon />
                                {t("connections.card.menu.test_connection")}
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={handleSyncModels} disabled={isSyncing}>
                                <RefreshCwIcon />
                                {t("connections.card.menu.sync_models")}
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => setEditOpen(true)}>
                                <PencilIcon />
                                {t("connections.card.menu.edit")}
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem variant="destructive" onClick={() => setDeleteOpen(true)}>
                                <Trash2Icon />
                                {t("connections.card.menu.delete")}
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                        
                    </DropdownMenu>
                </div>

                <div className="border-t p-4 flex flex-wrap items-center gap-4 justify-between bg-muted/25">
                    
                    <div className="flex items-center gap-2 flex-wrap text-sm">
                        {displayedModels.length > 0 ? (
                            <>
                                <p className="font-medium text-muted-foreground">{t("connections.card.available_models")}</p>
                                {displayedModels.map((m) => (
                                    <Badge key={m} variant="outline">
                                        {m}
                                    </Badge>
                                ))}
                                {extraModelsCount > 0 && <Badge variant="outline">+{extraModelsCount}</Badge>}
                            </>
                        ) : (
                            <span className="font-medium text-destructive">{t("connections.card.no_models")}</span>
                        )}
                    </div>
                    
                    <div className="sm:flex hidden">
                        <Button size="xs" variant="outline" onClick={handleSyncModels} disabled={isSyncing || isChecking}>
                            <RefreshCcwIcon className={`w-3.5 h-3.5 mr-1 ${isSyncing ? "animate-spin" : ""}`} />
                            <span>{t("connections.card.check_models")}</span>
                        </Button>
                    </div>

                </div>

            </div>

            <ManageConnectionForm connection={connection} open={editOpen} onOpenChange={setEditOpen} />
            <DeleteConnectionDialog connection={connection} open={deleteOpen} onOpenChange={setDeleteOpen} />
        </>
    )
}

export default ConnectionCard
