import { useTranslation } from "react-i18next"

import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import type { Chat } from "@/types/chats"

export interface UnpinChatDialogProps {
    chat: Chat
    open?: boolean
    onOpenChange?: (open: boolean) => void
    onUnpin?: (chatId: string) => void
}

export function UnpinChatDialog({ chat, open, onOpenChange, onUnpin }: UnpinChatDialogProps) {
    
    const { t } = useTranslation()

    const handleUnpin = () => {
        if (onUnpin) {
            onUnpin(chat.id)
        }
        if (onOpenChange) {
            onOpenChange(false)
        }
    }

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                
                <AlertDialogHeader>
                    <AlertDialogTitle>{t("chats.unpin.title")}</AlertDialogTitle>
                    <AlertDialogDescription>{t("chats.unpin.description", { name: chat.name })}</AlertDialogDescription>
                </AlertDialogHeader>
                
                <AlertDialogFooter>
                    <AlertDialogCancel>{t("chats.unpin.cancel_button")}</AlertDialogCancel>
                    <AlertDialogAction onClick={handleUnpin}>{t("chats.unpin.submit_button")}</AlertDialogAction>
                </AlertDialogFooter>

            </AlertDialogContent>
        </AlertDialog>
    )
}

export default UnpinChatDialog

