import { useTranslation } from "react-i18next"
import { CpuIcon, PlugZapIcon, RadioTowerIcon } from "lucide-react"

import { useConnectionsContext } from "@/context/connections"

export function ConnectionsSummary() {
    
    const { t } = useTranslation()
    const { connections, total } = useConnectionsContext()
    const modelCount = connections.reduce((count, connection) => count + (connection.models?.length ?? 0), 0)
    const providerCount = connections.filter((connection) => connection.type === "ollama").length
    
    const stats = [
        { label: t("connections.summary.total_connections"), value: total, detail: t("connections.summary.configured"), icon: PlugZapIcon, tone: "text-primary bg-primary/10 ring-primary/10" },
        { label: t("connections.summary.total_models"), value: modelCount, detail: t("connections.summary.detected"), icon: CpuIcon, tone: "text-primary bg-primary/10 ring-primary/10" },
        { label: t("connections.summary.providers"), value: providerCount, detail: t("connections.summary.ollama_provider"), icon: RadioTowerIcon, tone: "text-primary bg-primary/10 ring-primary/10" },
    ]

    return (
        <section aria-label={t("connections.summary.title")} className="sm:grid hidden gap-3 sm:grid-cols-3">
            {stats.map(({ label, value, detail, icon: Icon, tone }) => (
                <article key={label} className="group relative isolate overflow-hidden rounded-lg border bg-card p-4 hover:border-foreground/15">
                    <div aria-hidden="true" className="pointer-events-none absolute -right-8 -top-10 -z-10 size-28 rounded-full bg-primary/[0.04] blur-2xl transition-colors group-hover:bg-primary/[0.08]" />
                    <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0">
                            <p className="truncate text-xs font-medium uppercase text-muted-foreground">{label}</p>
                            <p className="mt-3 text-3xl font-semibold tracking-tight tabular-nums">{value}</p>
                            <p className="mt-1 text-xs text-muted-foreground">{detail}</p>
                        </div>
                        <div className={`flex size-10 shrink-0 items-center justify-center rounded-xl ring-1 ring-inset ${tone}`}>
                            <Icon className="size-[18px]" />
                        </div>
                    </div>
                </article>
            ))}
        </section>
    )
}

export default ConnectionsSummary
