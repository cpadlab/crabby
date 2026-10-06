import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"
import { SidebarContent, SidebarGroup, SidebarGroupContent, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar"
import { navMainItems } from "../../nav.config"
import { SidebarPinned } from "./pinned/component"
import { SidebarProjects } from "./projects/component"
import { SidebarChats } from "./chats/component"

export function LeftbarBody() {

    const { t } = useTranslation()

    return (
        <SidebarContent>
            
            <SidebarGroup>
                <SidebarGroupContent>
                    <SidebarMenu>
                        {navMainItems.map((item) => (
                            <SidebarMenuItem key={t(item.title)}>
                                <SidebarMenuButton tooltip={t(item.title)} render={item.url ? <Link to={item.url} /> : undefined}>
                                    <item.icon />
                                    <span>{t(item.title)}</span>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        ))}
                    </SidebarMenu>
                </SidebarGroupContent>
            </SidebarGroup>

            <SidebarPinned />
            <SidebarProjects />
            <SidebarChats />

        </SidebarContent>
    )
}

export default LeftbarBody
