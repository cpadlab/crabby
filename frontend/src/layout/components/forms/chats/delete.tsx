import { useTranslation } from "react-i18next"

import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import type { Chat } from "@/types/chats"

export interface DeleteChatDialogProps {
    chat: Chat
    open?: boolean
    onOpenChange?: (open: boolean) => void
}

export function DeleteChatDialog({ chat, open, onOpenChange }: DeleteChatDialogProps) {
    
    const { t } = useTranslation()

    const handleDelete = () => {
        if (onOpenChange) {
            onOpenChange(false)
        }
    }

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                
                <AlertDialogHeader>
                    <AlertDialogTitle>{t("chats.delete.title")}</AlertDialogTitle>
                    <AlertDialogDescription>{t("chats.delete.description", { name: chat.name })}</AlertDialogDescription>
                </AlertDialogHeader>
                
                <AlertDialogFooter>
                    <AlertDialogCancel>{t("chats.delete.cancel_button")}</AlertDialogCancel>
                    <AlertDialogAction variant="destructive" onClick={handleDelete}>{t("chats.delete.submit_button")}</AlertDialogAction>
                </AlertDialogFooter>

            </AlertDialogContent>
        </AlertDialog>
    )
}

export default DeleteChatDialog
