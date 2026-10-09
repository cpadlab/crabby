import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { useIsMobile } from "@/hooks/use-mobile"
import { ConnectionsSection } from "./components/sections/connections/section"

export function ConnectionsPage() {
    const { t } = useTranslation()
    const isMobile = useIsMobile()

    return (
        <main className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-5 py-6 sm:px-8 sm:py-10">
            
            <header className="space-y-5">
                
                <div className="flex items-center gap-2">
                    {isMobile && <SidebarTrigger />}
                    <Breadcrumb>
                        <BreadcrumbList>
                            <BreadcrumbItem>
                                <BreadcrumbLink render={<Link to="/" />}>{t("connections.breadcrumb_home")}</BreadcrumbLink>
                            </BreadcrumbItem>
                            <BreadcrumbSeparator />
                            <BreadcrumbItem>
                                <BreadcrumbPage>{t("connections.title")}</BreadcrumbPage>
                            </BreadcrumbItem>
                        </BreadcrumbList>
                    </Breadcrumb>
                </div>
                
                <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                    <div className="space-y-2">
                        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">{t("connections.title")}</h1>
                        <p className="max-w-2xl text-sm leading-6 text-muted-foreground">{t("connections.description")}</p>
                    </div>
                </div>

            </header>

            <ConnectionsSection />

        </main>
    )
}

export default ConnectionsPage
