import * as React from "react"
import { useTranslation } from "react-i18next"

import { SidebarGroup, SidebarGroupContent, SidebarMenu } from "@/components/ui/sidebar"
import { CreateProjectForm } from "@/layout/components/forms/project/create"
import { useProjects } from "@/hooks/use-projects"
import { ProjectsHeader } from "./header"
import { ProjectItem } from "./item"

export function SidebarProjects() {
    
    const { t } = useTranslation()
    const [isCreateOpen, setIsCreateOpen] = React.useState(false)
    const { projects } = useProjects()

    return (
        <>
            <SidebarGroup className="group-data-[collapsible=icon]:hidden">
                
                <ProjectsHeader setIsCreateOpen={setIsCreateOpen} />

                <SidebarGroupContent>
                    {projects.length === 0 ? (
                        <div className="px-3 text-xs text-muted-foreground">{t('projects.no_projects')}</div>
                    ) : (
                        <SidebarMenu>
                            {projects.map((project) => (
                                <ProjectItem key={project.id} project={project} />
                            ))}
                        </SidebarMenu>
                    )}
                </SidebarGroupContent>
            
            </SidebarGroup>

            <CreateProjectForm open={isCreateOpen} onOpenChange={setIsCreateOpen} />

        </>
    )
}

export default SidebarProjects
