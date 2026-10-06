import * as React from "react"
import { useTranslation } from "react-i18next"
import { MoreHorizontalIcon, PencilIcon, PinOffIcon } from "lucide-react"

import { SidebarMenuItem, SidebarMenuButton, SidebarMenuAction } from "@/components/ui/sidebar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { RenameChatForm } from "@/layout/components/forms/chats/rename"
import { UnpinChatDialog } from "@/layout/components/forms/chats/unpin"
import type { Chat } from "@/types/chats"

export interface PinnedItemProps {
    chat: Chat
    onUnpin: (chatId: string) => void
}

export function PinnedItem({ chat, onUnpin }: PinnedItemProps) {
    
    const { t } = useTranslation()
    const [isRenameOpen, setIsRenameOpen] = React.useState(false)
    const [isUnpinOpen, setIsUnpinOpen] = React.useState(false)

    return (
        <>
            <SidebarMenuItem className="group/pinned-item relative">
                
                <SidebarMenuButton tooltip={chat.name}>
                    <span className="truncate">{chat.name}</span>
                </SidebarMenuButton>

                <DropdownMenu>

                    <DropdownMenuTrigger
                        render={
                            <SidebarMenuAction className="right-1 bg-sidebar-accent text-muted-foreground opacity-0 group-hover/pinned-item:opacity-100 hover:opacity-100 focus:opacity-100 aria-expanded:opacity-100 transition-opacity" title={t("sidebar.pinned")}>
                                <MoreHorizontalIcon />
                            </SidebarMenuAction>
                        }
                    />

                    <DropdownMenuContent align="end" className="w-auto">

                        <DropdownMenuItem onClick={() => setIsRenameOpen(true)}>
                            <PencilIcon />
                            <span>{t("chats.menu.rename_chat")}</span>
                        </DropdownMenuItem>

                        <DropdownMenuItem onClick={() => setIsUnpinOpen(true)}>
                            <PinOffIcon />
                            <span>{t("chats.menu.unpin_chat")}</span>
                        </DropdownMenuItem>

                    </DropdownMenuContent>
                </DropdownMenu>

            </SidebarMenuItem>

            <RenameChatForm chat={chat} open={isRenameOpen} onOpenChange={setIsRenameOpen} />
            <UnpinChatDialog chat={chat} open={isUnpinOpen} onOpenChange={setIsUnpinOpen} onUnpin={onUnpin} />
        </>
    )
}

export default PinnedItem

