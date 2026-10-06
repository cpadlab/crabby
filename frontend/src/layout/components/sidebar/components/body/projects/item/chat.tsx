import * as React from "react"
import { useTranslation } from "react-i18next"
import { MoreHorizontalIcon, PencilIcon, TrashIcon } from "lucide-react"

import { SidebarMenuSubItem, SidebarMenuSubButton, SidebarMenuAction } from "@/components/ui/sidebar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { RenameChatForm } from "@/layout/components/forms/chats/rename"
import { DeleteChatDialog } from "@/layout/components/forms/chats/delete"
import type { Chat } from "@/types/chats"

export interface ProjectChatItemProps {
    chat: Chat
}

export function ProjectChatItem({ chat }: ProjectChatItemProps) {
    
    const { t } = useTranslation()
    const [isRenameOpen, setIsRenameOpen] = React.useState(false)
    const [isDeleteOpen, setIsDeleteOpen] = React.useState(false)

    return (
        <>
            <SidebarMenuSubItem className="w-full">
                
                <SidebarMenuSubButton className="w-full">
                    <span>{chat.name}</span>
                </SidebarMenuSubButton>

                <DropdownMenu>

                    <DropdownMenuTrigger
                        render={
                            <SidebarMenuAction className="right-1 bg-sidebar" showOnHover title={t("sidebar.projects")}>
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

            </SidebarMenuSubItem>

            <RenameChatForm chat={chat} open={isRenameOpen} onOpenChange={setIsRenameOpen} />
            <DeleteChatDialog chat={chat} open={isDeleteOpen} onOpenChange={setIsDeleteOpen} />
        </>
    )
}

export default ProjectChatItem

