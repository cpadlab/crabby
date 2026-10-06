import * as React from "react"
import type { Chat } from "@/types/chats"
import chatsMock from "@/assets/mocks/chats.json"

export function useChats() {
    
    const [chats, setChats] = React.useState<Chat[]>([])

    const sortByRecent = React.useCallback(() => {
        setChats((prev) =>
            [...prev].sort(
                (a, b) => new Date(b.modified).getTime() - new Date(a.modified).getTime()
            )
        )
    }, [])

    const sortByOldest = React.useCallback(() => {
        setChats((prev) =>
            [...prev].sort(
                (a, b) => new Date(a.modified).getTime() - new Date(b.modified).getTime()
            )
        )
    }, [])

    const loadChats = React.useCallback(() => {
        const loaded = chatsMock as Chat[]
        const sorted = [...loaded].sort(
            (a, b) => new Date(b.modified).getTime() - new Date(a.modified).getTime()
        )
        setChats(sorted)
    }, [])

    React.useEffect(() => {
        loadChats()
    }, [loadChats])

    const handleCreateChat = (name?: string) => {
        const newChat: Chat = {
            id: `chat_${Date.now()}`,
            name: name?.trim() || `Nuevo Chat`,
            modified: new Date().toISOString(),
            pinned: false,
        }

        setChats((prev) => [newChat, ...prev])
    }

    const handleUnpinChat = (chatId: string) => {
        setChats((prev) =>
            prev.map((c) => (c.id === chatId ? { ...c, pinned: false } : c))
        )
    }

    const pinnedChats = React.useMemo(() => chats.filter((c) => c.pinned), [chats])
    const unpinnedChats = React.useMemo(() => chats.filter((c) => !c.pinned), [chats])

    return {
        chats,
        pinnedChats,
        unpinnedChats,
        setChats,
        loadChats,
        sortByRecent,
        sortByOldest,
        handleCreateChat,
        handleUnpinChat,
    }
}

export default useChats

