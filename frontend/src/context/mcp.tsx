import * as React from "react"

import { useMCP, type UseMCPReturn } from "@/hooks/use-mcp"

const MCPContext = React.createContext<UseMCPReturn | undefined>(undefined)
MCPContext.displayName = "MCPContext"

export interface MCPProviderProps {
    children: React.ReactNode
}

export function MCPProvider({ children }: MCPProviderProps) {
    
    const value = useMCP()
    
    return (
        <MCPContext.Provider value={value}>
            {children}
        </MCPContext.Provider>
    )
}

export function useMCPContext(): UseMCPReturn {
    
    const context = React.useContext(MCPContext)
    
    if (context === undefined) {
        throw new Error("useMCPContext must be used within an MCPProvider")
    }
    
    return context

}

export default MCPProvider
