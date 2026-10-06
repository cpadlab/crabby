import { useTranslation } from "react-i18next"

import { SidebarMenuItem, SidebarMenuSub, SidebarMenuSubItem } from "@/components/ui/sidebar"
import { Collapsible, CollapsibleContent } from "@/components/ui/collapsible"
import { ProjectItemRow } from "./project"
import { ProjectChatItem } from "./chat"
import type { Project } from "@/types/projects"

export interface ProjectItemProps {
    project: Project
}

export function ProjectItem({ project }: ProjectItemProps) {
    
    const { t } = useTranslation()
    const visibleChats = project.chats.filter((chat) => !chat.pinned)

    return (
        <Collapsible defaultOpen className="group/collapsible">
            <SidebarMenuItem>
                
                <ProjectItemRow project={project} />

                <CollapsibleContent>
                    <SidebarMenuSub className="w-full">
                        {visibleChats.length === 0 ? (
                            <SidebarMenuSubItem className="w-full">
                                <div className="px-2 text-xs text-muted-foreground">
                                    {t('projects.no_chats')}
                                </div>
                            </SidebarMenuSubItem>
                        ) : (
                            visibleChats.map((chat) => (
                                <ProjectChatItem key={chat.id} chat={chat} />
                            ))
                        )}
                    </SidebarMenuSub>
                </CollapsibleContent>

            </SidebarMenuItem>
        </Collapsible>
    )
}

export default ProjectItem
