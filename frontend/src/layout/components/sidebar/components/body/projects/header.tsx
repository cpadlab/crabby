import { useTranslation } from "react-i18next"
import { MoreHorizontalIcon, PlusIcon, ArrowUpDownIcon, ClockIcon, HistoryIcon } from "lucide-react"

import { SidebarGroupAction, SidebarGroupLabel } from "@/components/ui/sidebar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { CreateProjectForm } from "@/layout/components/forms/create-project"
import { useProjects } from "@/hooks/use-projects"

export interface ProjectsHeaderProps {
    setIsCreateOpen: (open: boolean) => void
}

export function ProjectsHeader({ setIsCreateOpen }: ProjectsHeaderProps) {
    
    const { t } = useTranslation()
    const { sortByRecent, sortByOldest } = useProjects()

    return (
        <>
            <SidebarGroupLabel>{t('sidebar.projects')}</SidebarGroupLabel>

            <DropdownMenu>

                <DropdownMenuTrigger
                    render={
                        <SidebarGroupAction className="text-muted-foreground" title={t('sidebar.projects')}>
                            <MoreHorizontalIcon />
                        </SidebarGroupAction>
                    }
                />

                <DropdownMenuContent align="end" className="w-auto">
                    
                    <DropdownMenuItem onClick={() => setIsCreateOpen(true)}>
                        <PlusIcon />
                        <span>{t('projects.menu.new_project')}</span>
                    </DropdownMenuItem>

                    <DropdownMenuSub>
                        <DropdownMenuSubTrigger>
                            <ArrowUpDownIcon />
                            <span>{t('projects.menu.sort_by')}</span>
                        </DropdownMenuSubTrigger>
                        <DropdownMenuSubContent>
                            <DropdownMenuItem onClick={sortByRecent}>
                                <ClockIcon />
                                <span>{t('projects.menu.sort_recent')}</span>
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={sortByOldest}>
                                <HistoryIcon />
                                <span>{t('projects.menu.sort_oldest')}</span>
                            </DropdownMenuItem>
                        </DropdownMenuSubContent>
                    </DropdownMenuSub>

                </DropdownMenuContent>
                
            </DropdownMenu>

            <CreateProjectForm
                trigger={
                    <SidebarGroupAction className="text-muted-foreground right-8" title={t('sidebar.projects')}>
                        <PlusIcon />
                    </SidebarGroupAction>
                }
            />
        </>
    )
}

export default ProjectsHeader
