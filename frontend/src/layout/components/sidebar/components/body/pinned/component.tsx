import { useTranslation } from "react-i18next"

import { SidebarGroup, SidebarGroupContent, SidebarMenu } from "@/components/ui/sidebar"
import { Collapsible, CollapsibleContent } from "@/components/ui/collapsible"
import { useChats } from "@/hooks/use-chats"
import { PinnedHeader } from "./header"
import { PinnedItem } from "./item"

export function SidebarPinned() {
    
    const { t } = useTranslation()
    const { pinnedChats, sortByRecent, sortByOldest, handleUnpinChat } = useChats()

    return (
        <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroup className="group-data-[collapsible=icon]:hidden">
                
                <PinnedHeader sortByRecent={sortByRecent} sortByOldest={sortByOldest} />

                <SidebarGroupContent>
                    <CollapsibleContent>
                        {pinnedChats.length === 0 ? (
                            <div className="px-3 text-xs text-muted-foreground">{t("chats.no_pinned")}</div>
                        ) : (
                            <SidebarMenu>
                                {pinnedChats.map((chat) => (
                                    <PinnedItem key={chat.id} chat={chat} onUnpin={handleUnpinChat} />
                                ))}
                            </SidebarMenu>
                        )}
                    </CollapsibleContent>
                </SidebarGroupContent>
            
            </SidebarGroup>
        </Collapsible>
    )
}

export default SidebarPinned

