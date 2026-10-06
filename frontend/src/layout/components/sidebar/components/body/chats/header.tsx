import { useTranslation } from "react-i18next"
import { MoreHorizontalIcon, PlusIcon, ArrowUpDownIcon, ClockIcon, HistoryIcon } from "lucide-react"

import { SidebarGroupAction, SidebarGroupLabel } from "@/components/ui/sidebar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export interface ChatsHeaderProps {
    onCreateChat: () => void
    sortByRecent: () => void
    sortByOldest: () => void
}

export function ChatsHeader({ onCreateChat, sortByRecent, sortByOldest }: ChatsHeaderProps) {
    
    const { t } = useTranslation()

    return (
        <>
            <SidebarGroupLabel>{t("sidebar.chats")}</SidebarGroupLabel>

            <DropdownMenu>

                <DropdownMenuTrigger
                    render={
                        <SidebarGroupAction className="text-muted-foreground" title={t("sidebar.chats")}>
                            <MoreHorizontalIcon />
                        </SidebarGroupAction>
                    }
                />

                <DropdownMenuContent align="end" className="w-auto">
                    
                    <DropdownMenuItem onClick={onCreateChat}>
                        <PlusIcon />
                        <span>{t("chats.menu.new_chat")}</span>
                    </DropdownMenuItem>

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

            <SidebarGroupAction className="text-muted-foreground right-8" title={t("chats.menu.new_chat")} onClick={onCreateChat}>
                <PlusIcon />
            </SidebarGroupAction>
        </>
    )
}

export default ChatsHeader

