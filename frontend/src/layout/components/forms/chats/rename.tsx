import * as React from "react"
import { useTranslation } from "react-i18next"
import { MessageSquareTextIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group"
import { Label } from "@/components/ui/label"
import type { Chat } from "@/types/chats"

export interface RenameChatFormProps {
    chat: Chat
    open?: boolean
    onOpenChange?: (open: boolean) => void
    trigger?: React.ReactNode
}

export function RenameChatForm({ chat, open, onOpenChange, trigger }: RenameChatFormProps) {
    
    const { t } = useTranslation()
    const [name, setName] = React.useState(chat.name)

    React.useEffect(() => {
        setName(chat.name)
    }, [chat.name])

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (onOpenChange) {
            onOpenChange(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
      
            {trigger && (
                <DialogTrigger render={trigger as React.ReactElement} />
            )}

            <DialogContent>
                
                <DialogHeader>
                    <DialogTitle>{t("chats.rename.title")}</DialogTitle>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                    <div className="flex flex-col gap-2">
                        <Label htmlFor="rename-chat-name">{t("chats.rename.name_label")}</Label>
                        <InputGroup>
                            <InputGroupAddon align="inline-start">
                                <MessageSquareTextIcon />
                            </InputGroupAddon>
                            <InputGroupInput id="rename-chat-name" value={name} onChange={(e) => setName(e.target.value)} placeholder={t("chats.rename.placeholder")} />
                        </InputGroup>
                    </div>

                    <DialogFooter>
                        <Button type="submit">{t("chats.rename.submit_button")}</Button>
                    </DialogFooter>

                </form>
            </DialogContent>
        
        </Dialog>
    )
}

export default RenameChatForm

