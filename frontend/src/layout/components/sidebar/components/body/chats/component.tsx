import { useTranslation } from "react-i18next"

import { SidebarGroup, SidebarGroupContent, SidebarMenu } from "@/components/ui/sidebar"
import { useChats } from "@/hooks/use-chats"
import { ChatsHeader } from "./header"
import { StandaloneChatItem } from "./item"

export function SidebarChats() {
    
    const { t } = useTranslation()
    const { unpinnedChats, handleCreateChat, sortByRecent, sortByOldest } = useChats()

    return (
        <SidebarGroup className="group-data-[collapsible=icon]:hidden">
            
            <ChatsHeader onCreateChat={() => handleCreateChat()} sortByRecent={sortByRecent} sortByOldest={sortByOldest} />

            <SidebarGroupContent>
                {unpinnedChats.length === 0 ? (
                    <div className="px-3 text-xs text-muted-foreground">{t("chats.no_chats")}</div>
                ) : (
                    <SidebarMenu>
                        {unpinnedChats.map((chat) => (
                            <StandaloneChatItem key={chat.id} chat={chat} />
                        ))}
                    </SidebarMenu>
                )}
            </SidebarGroupContent>
        
        </SidebarGroup>
    )
}

export default SidebarChats

