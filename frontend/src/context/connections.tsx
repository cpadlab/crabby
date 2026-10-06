import * as React from "react"
import { useConnections, type UseConnectionsReturn } from "@/hooks/use-connections"

const ConnectionsContext = React.createContext<UseConnectionsReturn | null>(null)

export interface ConnectionsProviderProps {
    children: React.ReactNode
}

export function ConnectionsProvider({ children }: ConnectionsProviderProps) {
    const connectionsState = useConnections()

    return (
        <ConnectionsContext.Provider value={connectionsState}>
            {children}
        </ConnectionsContext.Provider>
    )
}

export function useConnectionsContext(): UseConnectionsReturn {
    
    const context = React.useContext(ConnectionsContext)
    
    if (!context) {
        throw new Error("useConnectionsContext must be used within a ConnectionsProvider")
    }
    
    return context

}

export default ConnectionsProvider

