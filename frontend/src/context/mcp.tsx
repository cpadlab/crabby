import * as React from "react"
import { useMCP, type UseMCPReturn } from "@/hooks/use-mcp"

const MCPContext = React.createContext<UseMCPReturn | null>(null)

export interface MCPProviderProps {
    children: React.ReactNode
}

export function MCPProvider({ children }: MCPProviderProps) {
    
    const mcpState = useMCP()

    return (
        <MCPContext.Provider value={mcpState}>
            {children}
        </MCPContext.Provider>
    )
    
}

export function useMCPContext(): UseMCPReturn {
    const context = React.useContext(MCPContext)

    if (!context) {
        throw new Error("useMCPContext must be used within an MCPProvider")
    }

    return context
}

export default MCPProvider

