import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"
import { PlusIcon } from "lucide-react"
import { SidebarContent, SidebarGroup, SidebarGroupAction, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar"
import { CreateProjectForm } from "@/layout/components/forms/create-project"
import { navMainItems } from "../nav.config"

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

            <SidebarGroup>
                <SidebarGroupLabel>{t('sidebar.projects')}</SidebarGroupLabel>
                <CreateProjectForm
                    trigger={
                        <SidebarGroupAction title={t('sidebar.projects')}>
                            <PlusIcon />
                        </SidebarGroupAction>
                    }
                />
                <SidebarGroupContent />
            </SidebarGroup>

        </SidebarContent>
    )
}

export default LeftbarBody
