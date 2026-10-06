import { SquarePenIcon, SearchIcon, PlugZapIcon, BotIcon } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

export interface NavItem {
    title: string
    icon: LucideIcon
    url?: string
}

export const navMainItems: NavItem[] = [
    {
        title: 'sidebar.new_conversation',
        icon: SquarePenIcon,
        url: '/',
    },
    {
        title: 'sidebar.search_conversations',
        icon: SearchIcon,
    },
    {
        title: 'sidebar.my_connections',
        icon: PlugZapIcon,
        url: '/connections',
    },
    {
        title: 'sidebar.my_agents',
        icon: BotIcon,
        url: '/agents',
    },
]

