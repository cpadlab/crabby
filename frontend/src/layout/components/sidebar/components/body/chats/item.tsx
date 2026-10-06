import * as React from "react"
import { useTranslation } from "react-i18next"
import { MoreHorizontalIcon, PencilIcon, TrashIcon } from "lucide-react"

import { SidebarMenuItem, SidebarMenuButton, SidebarMenuAction } from "@/components/ui/sidebar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { RenameChatForm } from "@/layout/components/forms/chats/rename"
import { DeleteChatDialog } from "@/layout/components/forms/chats/delete"
import type { Chat } from "@/types/chats"

export interface StandaloneChatItemProps {
    chat: Chat
}

export function StandaloneChatItem({ chat }: StandaloneChatItemProps) {
    
    const { t } = useTranslation()
    const [isRenameOpen, setIsRenameOpen] = React.useState(false)
    const [isDeleteOpen, setIsDeleteOpen] = React.useState(false)

    return (
        <>
            <SidebarMenuItem className="group/chat-section-item relative">
                
                <SidebarMenuButton tooltip={chat.name}>
                    <span className="truncate">{chat.name}</span>
                </SidebarMenuButton>

                <DropdownMenu>

                    <DropdownMenuTrigger
                        render={
                            <SidebarMenuAction className="right-1 bg-sidebar-accent text-muted-foreground opacity-0 group-hover/chat-section-item:opacity-100 hover:opacity-100 focus:opacity-100 aria-expanded:opacity-100 transition-opacity" title={t("sidebar.chats")}>
                                <MoreHorizontalIcon />
                            </SidebarMenuAction>
                        }
                    />

                    <DropdownMenuContent align="end" className="w-auto">

                        <DropdownMenuItem onClick={() => setIsRenameOpen(true)}>
                            <PencilIcon />
                            <span>{t("chats.menu.rename_chat")}</span>
                        </DropdownMenuItem>

                        <DropdownMenuItem variant="destructive" onClick={() => setIsDeleteOpen(true)}>
                            <TrashIcon />
                            <span>{t("chats.menu.delete_chat")}</span>
                        </DropdownMenuItem>

                    </DropdownMenuContent>
                </DropdownMenu>

            </SidebarMenuItem>

            <RenameChatForm chat={chat} open={isRenameOpen} onOpenChange={setIsRenameOpen} />
            <DeleteChatDialog chat={chat} open={isDeleteOpen} onOpenChange={setIsDeleteOpen} />
        </>
    )
}

export default StandaloneChatItem

