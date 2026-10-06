import { SidebarTrigger } from "@/components/ui/sidebar"
import { useIsMobile } from "@/hooks/use-mobile"
import { useTranslation } from "react-i18next"

export function ConnectionsPage() {
    
    const { t } = useTranslation()
    const isMobile = useIsMobile()

    return (
        <div className="flex flex-col gap-2 xl:w-[50%] w-[90%] py-6 md:w-[75%] mx-auto">
            
            <div>
                <div className="flex items-center gap-2">
                    {isMobile && <SidebarTrigger />}
                    <h1 className="text-2xl font-bold">{t("connections.title")}</h1>
                </div>
                <p className="text-base text-muted-foreground">{t("connections.description")}</p>
            </div>

        </div>
    )
}

export default ConnectionsPage