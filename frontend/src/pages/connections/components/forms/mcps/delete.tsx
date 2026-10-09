import * as React from "react"
import { useTranslation } from "react-i18next"

import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { useMCPContext } from "@/context/mcp"
import type { MCPServer } from "@/types/mcp"

export interface DeleteMCPDialogProps {
    server: MCPServer
    open?: boolean
    onOpenChange?: (open: boolean) => void
    onSuccess?: () => void
}

export function DeleteMCPDialog({ server, open, onOpenChange, onSuccess }: DeleteMCPDialogProps) {
    
    const { t } = useTranslation()
    const { deleteMCPServer } = useMCPContext()
    const [isDeleting, setIsDeleting] = React.useState(false)

    const handleDelete = async () => {
        setIsDeleting(true)
        try {
            const response = await deleteMCPServer(server.id)
            if (response.success) {
                onSuccess?.()
                onOpenChange?.(false)
            }
        } finally {
            setIsDeleting(false)
        }
    }

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                
                <AlertDialogHeader>
                    <AlertDialogTitle>{t("mcp.delete.title")}</AlertDialogTitle>
                    <AlertDialogDescription>{t("mcp.delete.description", { name: server.name })}</AlertDialogDescription>
                </AlertDialogHeader>
                
                <AlertDialogFooter>
                    <AlertDialogCancel disabled={isDeleting}>{t("mcp.delete.cancel_button")}</AlertDialogCancel>
                    <AlertDialogAction variant="destructive" disabled={isDeleting} onClick={handleDelete}>
                        {t("mcp.delete.submit_button")}
                    </AlertDialogAction>
                </AlertDialogFooter>

            </AlertDialogContent>
        </AlertDialog>
    )
}

export default DeleteMCPDialog
