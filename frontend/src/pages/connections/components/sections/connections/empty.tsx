import { useTranslation } from "react-i18next"
import { PlugIcon, PlusIcon } from "lucide-react"

import { Button } from "@/components/ui/button"

export interface ConnectionsEmptyStateProps {
    onCreateClick?: () => void
}

export function ConnectionsEmptyState({ onCreateClick }: ConnectionsEmptyStateProps) {
    
    const { t } = useTranslation()

    return (
        <div className="flex flex-col items-center justify-center p-8 text-center border border-dashed rounded-4xl bg-muted/20 gap-3">
            
            <div className="p-3 bg-muted rounded-full text-muted-foreground">
                <PlugIcon className="w-6 h-6" />
            </div>
            
            <div className="flex flex-col gap-1 max-w-md">
                <h3 className="font-semibold text-base">{t("connections.section.empty_title")}</h3>
                <p className="text-sm text-muted-foreground">
                    {t("connections.section.empty_description")}
                </p>
            </div>
            
            {onCreateClick && (
                <Button size="sm" onClick={onCreateClick} className="mt-1">
                    <PlusIcon />
                    {t("connections.section.create_button")}
                </Button>
            )}

        </div>
    )
}

export default ConnectionsEmptyState

