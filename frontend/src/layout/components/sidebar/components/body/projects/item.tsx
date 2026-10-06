import { ChevronRightIcon, FolderIcon, MessageSquareIcon } from "lucide-react"

import { SidebarMenuItem, SidebarMenuButton, SidebarMenuSub, SidebarMenuSubItem, SidebarMenuSubButton } from "@/components/ui/sidebar"
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible"
import type { Project } from "@/types/projects"

export interface ProjectItemProps {
    project: Project
}

export function ProjectItem({ project }: ProjectItemProps) {
    
    return (
        <Collapsible className="group/collapsible">
            <SidebarMenuItem>
                
                <CollapsibleTrigger
                    render={
                        <SidebarMenuButton tooltip={project.name}>
                            <span className="truncate">{project.name}</span>
                            <ChevronRightIcon className="text-muted-foreground" />
                        </SidebarMenuButton>
                    }
                />
                
                <CollapsibleContent>
                    <SidebarMenuSub className="w-full">
                        {project.chats.map((chat) => (
                            <SidebarMenuSubItem key={chat.id} className="w-full">
                                <SidebarMenuSubButton className="w-full">
                                    <span>{chat.name}</span>
                                </SidebarMenuSubButton>
                            </SidebarMenuSubItem>
                        ))}
                    </SidebarMenuSub>
                </CollapsibleContent>

            </SidebarMenuItem>
        </Collapsible>
    )
}

export default ProjectItem
