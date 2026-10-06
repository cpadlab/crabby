import { useTranslation } from "react-i18next"

import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import type { Project } from "@/types/projects"

export interface DeleteProjectDialogProps {
    project: Project
    open?: boolean
    onOpenChange?: (open: boolean) => void
}

export function DeleteProjectDialog({ project, open, onOpenChange }: DeleteProjectDialogProps) {
    
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
                    <AlertDialogTitle>{t("projects.delete.title")}</AlertDialogTitle>
                    <AlertDialogDescription>{t("projects.delete.description")}</AlertDialogDescription>
                </AlertDialogHeader>
                
                <AlertDialogFooter>
                    <AlertDialogCancel>{t("projects.delete.cancel_button")}</AlertDialogCancel>
                    <AlertDialogAction variant="destructive" onClick={handleDelete}>{t("projects.delete.submit_button")}</AlertDialogAction>
                </AlertDialogFooter>

            </AlertDialogContent>
        </AlertDialog>
    )
}

export default DeleteProjectDialog
