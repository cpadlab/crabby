import * as React from "react"

import { SidebarGroup, SidebarGroupContent, SidebarMenu } from "@/components/ui/sidebar"
import { CreateProjectForm } from "@/layout/components/forms/project/create"
import { useProjects } from "@/hooks/use-projects"
import { ProjectsHeader } from "./header"
import { ProjectItem } from "./item"

export function SidebarProjects() {
    
    const [isCreateOpen, setIsCreateOpen] = React.useState(false)
    const { projects } = useProjects()

    return (
        <>
            <SidebarGroup>
                
                <ProjectsHeader setIsCreateOpen={setIsCreateOpen} />

                <SidebarGroupContent>
                    <SidebarMenu>
                        {projects.map((project) => (
                            <ProjectItem key={project.id} project={project} />
                        ))}
                    </SidebarMenu>
                </SidebarGroupContent>
            
            </SidebarGroup>

            <CreateProjectForm open={isCreateOpen} onOpenChange={setIsCreateOpen} />

        </>
    )
}

export default SidebarProjects
