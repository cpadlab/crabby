import { Trans, useTranslation } from "react-i18next"

import { SidebarTrigger } from "@/components/ui/sidebar"
import { useIsMobile } from "@/hooks/use-mobile"
import { ConnectionsSection } from "./components/sections/connections/section"

export function ConnectionsPage() {
    
    const { t } = useTranslation()
    const isMobile = useIsMobile()

    return (
        <div className="flex flex-col gap-6 xl:w-[50%] w-[90%] md:py-12 py-4 md:w-[75%] mx-auto">
            
            <div>
                <div className="flex items-center gap-2">
                    {isMobile && <SidebarTrigger />}
                    <h1 className="text-3xl font-bold">{t("connections.title")}</h1>
                </div>
                <p className="text-base text-muted-foreground">
                    <Trans
                        i18nKey="connections.description"
                        components={{
                            1: (<a href="https://modelcontextprotocol.io" target="_blank" rel="noreferrer" className="border-b border-muted-foreground/60 hover:border-foreground transition-colors" />),
                        }} />
                </p>
            </div>

            <ConnectionsSection />
           
        </div>
    )
}

export default ConnectionsPage