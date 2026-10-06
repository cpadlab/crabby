import * as React from "react"
import { useTranslation } from "react-i18next"

import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { useConnectionsContext } from "@/context/connections"
import type { Connection } from "@/types/connections"

export interface DeleteConnectionDialogProps {
    connection: Connection
    open?: boolean
    onOpenChange?: (open: boolean) => void
    onSuccess?: () => void
}

export function DeleteConnectionDialog({
    connection,
    open,
    onOpenChange,
    onSuccess,
}: DeleteConnectionDialogProps) {

    const { t } = useTranslation()
    const { deleteConnection } = useConnectionsContext()
    const [isDeleting, setIsDeleting] = React.useState(false)

    const handleDelete = async () => {
        setIsDeleting(true)
        try {
            const res = await deleteConnection(connection.id)
            if (res.success) {
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
                    <AlertDialogTitle>{t("connections.delete.title")}</AlertDialogTitle>
                    <AlertDialogDescription>
                        {t("connections.delete.description", { name: connection.name })}
                    </AlertDialogDescription>
                </AlertDialogHeader>

                <AlertDialogFooter>
                    <AlertDialogCancel disabled={isDeleting}>
                        {t("connections.delete.cancel_button")}
                    </AlertDialogCancel>
                    <AlertDialogAction variant="destructive" disabled={isDeleting} onClick={handleDelete}>
                        {t("connections.delete.submit_button")}
                    </AlertDialogAction>
                </AlertDialogFooter>

            </AlertDialogContent>
        </AlertDialog>
    )
}

export default DeleteConnectionDialog

