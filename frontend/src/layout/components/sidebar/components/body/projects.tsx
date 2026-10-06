import { useTranslation } from "react-i18next"
import { PlusIcon } from "lucide-react"
import { SidebarGroup, SidebarGroupAction, SidebarGroupContent, SidebarGroupLabel } from "@/components/ui/sidebar"
import { CreateProjectForm } from "@/layout/components/forms/create-project"

export function SidebarProjects() {
    
    const { t } = useTranslation()

    return (
        <SidebarGroup>
            
            <SidebarGroupLabel>{t('sidebar.projects')}</SidebarGroupLabel>
            
            <CreateProjectForm
                trigger={
                    <SidebarGroupAction title={t('sidebar.projects')}>
                        <PlusIcon />
                    </SidebarGroupAction>
                }
            />
            
            <SidebarGroupContent />ç
            
        </SidebarGroup>
    )
}

export default SidebarProjects

