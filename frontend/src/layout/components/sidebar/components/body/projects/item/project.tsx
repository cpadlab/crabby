import * as React from "react"
import { useTranslation } from "react-i18next"
import { ChevronRightIcon, MoreHorizontalIcon, PlusIcon, PencilIcon, TrashIcon } from "lucide-react"

import { SidebarMenuButton, SidebarMenuAction } from "@/components/ui/sidebar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { CollapsibleTrigger } from "@/components/ui/collapsible"
import { RenameProjectForm } from "@/layout/components/forms/project/rename"
import { DeleteProjectDialog } from "@/layout/components/forms/project/delete"
import type { Project } from "@/types/projects"

export interface ProjectItemRowProps {
    project: Project
}

export function ProjectItemRow({ project }: ProjectItemRowProps) {
    
    const { t } = useTranslation()
    const [isRenameOpen, setIsRenameOpen] = React.useState(false)
    const [isDeleteOpen, setIsDeleteOpen] = React.useState(false)

    return (
        <div className="group/project-header relative flex w-full items-center">
            <CollapsibleTrigger
                render={
                    <SidebarMenuButton tooltip={project.name}>
                        <span className="truncate">{project.name}</span>
                        <ChevronRightIcon className="text-muted-foreground" />
                    </SidebarMenuButton>
                }
            />

            <SidebarMenuAction className="right-7 text-muted-foreground opacity-0 group-hover/project-header:opacity-100 hover:opacity-100 focus:opacity-100 aria-expanded:opacity-100 bg-sidebar-accent" title={t("projects.menu.new_chat")}>
                <PlusIcon />
            </SidebarMenuAction>

            <DropdownMenu>

                <DropdownMenuTrigger
                    render={
                        <SidebarMenuAction className="right-1 bg-sidebar-accent text-muted-foreground opacity-0 group-hover/project-header:opacity-100 hover:opacity-100 focus:opacity-100 aria-expanded:opacity-100" title={t("sidebar.projects")}>
                            <MoreHorizontalIcon />
                        </SidebarMenuAction>
                    }
                />

                <DropdownMenuContent align="end" className="w-auto">

                    <DropdownMenuItem>
                        <PlusIcon />
                        <span>{t("projects.menu.new_chat")}</span>
                    </DropdownMenuItem>

                    <DropdownMenuItem onClick={() => setIsRenameOpen(true)}>
                        <PencilIcon />
                        <span>{t("projects.menu.rename_project")}</span>
                    </DropdownMenuItem>

                    <DropdownMenuItem variant="destructive" onClick={() => setIsDeleteOpen(true)}>
                        <TrashIcon />
                        <span>{t("projects.menu.delete_project")}</span>
                    </DropdownMenuItem>

                </DropdownMenuContent>
            </DropdownMenu>

            <RenameProjectForm project={project} open={isRenameOpen} onOpenChange={setIsRenameOpen} />
            <DeleteProjectDialog project={project} open={isDeleteOpen} onOpenChange={setIsDeleteOpen} />
        </div>
    )
}

export default ProjectItemRow