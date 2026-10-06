import * as React from "react"
import { SidebarGroup, SidebarGroupContent } from "@/components/ui/sidebar"
import { CreateProjectForm } from "@/layout/components/forms/create-project"
import { ProjectsHeader } from "./header"

export function SidebarProjects() {
    
    const [isCreateOpen, setIsCreateOpen] = React.useState(false)

    return (
        <>
            <SidebarGroup>
                
                <ProjectsHeader setIsCreateOpen={setIsCreateOpen} />
                <SidebarGroupContent />
            
            </SidebarGroup>

            <CreateProjectForm open={isCreateOpen} onOpenChange={setIsCreateOpen} />

        </>
    )
}

export default SidebarProjects
