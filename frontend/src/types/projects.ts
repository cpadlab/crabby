import type { Chat } from "./chats"

export interface Project {
    id: string
    name: string
    modified: string
    chats: Chat[]
}

