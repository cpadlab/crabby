import { useTranslation } from "react-i18next"
import { CpuIcon, PlugIcon, ServerIcon } from "lucide-react"

import { useConnectionsContext } from "@/context/connections"

export function ConnectionsSummary() {

    const { t } = useTranslation()
    const { connections, total } = useConnectionsContext()

    const totalModels = connections.reduce((acc, c) => acc + (c.models?.length || 0), 0)
    const ollamaCount = connections.filter((c) => c.type === "ollama").length

    return (
        <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            
            <div className="bg-card border rounded-3xl p-4 flex items-center gap-4 transition-colors hover:border-border/80">
                <div className="p-3 bg-muted rounded-2xl text-muted-foreground shrink-0">
                    <PlugIcon className="w-5 h-5" />
                </div>
                <div className="flex flex-col min-w-0">
                    <span className="text-xs font-medium text-muted-foreground uppercase truncate">
                        {t("connections.summary.total_connections")}
                    </span>
                    <div className="flex items-baseline gap-2 mt-0.5">
                        <span className="text-2xl font-bold ">{total}</span>
                        <span className="text-xs text-muted-foreground">{t("connections.summary.configured")}</span>
                    </div>
                </div>
            </div>

            <div className="bg-card border rounded-3xl p-4 flex items-center gap-4 transition-colors hover:border-border/80">
                <div className="p-3 bg-muted rounded-2xl text-muted-foreground shrink-0">
                    <CpuIcon className="w-5 h-5" />
                </div>
                <div className="flex flex-col min-w-0">
                    <span className="text-xs font-medium text-muted-foreground uppercase  truncate">
                        {t("connections.summary.total_models")}
                    </span>
                    <div className="flex items-baseline gap-2 mt-0.5">
                        <span className="text-2xl font-bold ">{totalModels}</span>
                        <span className="text-xs text-muted-foreground">{t("connections.summary.detected")}</span>
                    </div>
                </div>
            </div>

            <div className="bg-card border rounded-3xl p-4 flex items-center gap-4 transition-colors hover:border-border/80">
                <div className="p-3 bg-muted rounded-2xl text-muted-foreground shrink-0">
                    <ServerIcon className="w-5 h-5" />
                </div>
                <div className="flex flex-col min-w-0">
                    <span className="text-xs font-medium text-muted-foreground uppercase  truncate">
                        {t("connections.summary.providers")}
                    </span>
                    <div className="flex items-baseline gap-2 mt-0.5">
                        <span className="text-2xl font-bold">{ollamaCount}</span>
                        <span className="text-xs text-muted-foreground">Ollama</span>
                    </div>
                </div>
            </div>
            
        </section>
    )
}