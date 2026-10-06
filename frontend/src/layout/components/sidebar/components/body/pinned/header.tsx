import { useTranslation } from "react-i18next"
import { MoreHorizontalIcon, ArrowUpDownIcon, ClockIcon, HistoryIcon } from "lucide-react"

import { SidebarGroupAction, SidebarGroupLabel } from "@/components/ui/sidebar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export interface PinnedHeaderProps {
    sortByRecent: () => void
    sortByOldest: () => void
}

export function PinnedHeader({ sortByRecent, sortByOldest }: PinnedHeaderProps) {
    
    const { t } = useTranslation()

    return (
        <>
            <SidebarGroupLabel>{t("sidebar.pinned")}</SidebarGroupLabel>

            <DropdownMenu>

                <DropdownMenuTrigger
                    render={
                        <SidebarGroupAction className="text-muted-foreground" title={t("sidebar.pinned")}>
                            <MoreHorizontalIcon />
                        </SidebarGroupAction>
                    }
                />

                <DropdownMenuContent align="end" className="w-auto">
                    
                    <DropdownMenuSub>
                        <DropdownMenuSubTrigger>
                            <ArrowUpDownIcon />
                            <span>{t("chats.menu.sort_by")}</span>
                        </DropdownMenuSubTrigger>
                        <DropdownMenuSubContent>
                            <DropdownMenuItem onClick={sortByRecent}>
                                <ClockIcon />
                                <span>{t("chats.menu.sort_recent")}</span>
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={sortByOldest}>
                                <HistoryIcon />
                                <span>{t("chats.menu.sort_oldest")}</span>
                            </DropdownMenuItem>
                        </DropdownMenuSubContent>
                    </DropdownMenuSub>

                </DropdownMenuContent>
                
            </DropdownMenu>
        </>
    )
}

export default PinnedHeader

