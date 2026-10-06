import * as React from "react"
import { useTranslation } from "react-i18next"
import { FolderPenIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group"
import { Label } from "@/components/ui/label"
import type { Project } from "@/types/projects"

export interface RenameProjectFormProps {
    project: Project
    open?: boolean
    onOpenChange?: (open: boolean) => void
    trigger?: React.ReactNode
}

export function RenameProjectForm({ project, open, onOpenChange, trigger }: RenameProjectFormProps) {
    
    const { t } = useTranslation()
    const [name, setName] = React.useState(project.name)

    React.useEffect(() => {
        setName(project.name)
    }, [project.name])

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
                    <DialogTitle>{t("projects.rename.title")}</DialogTitle>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                    <div className="flex flex-col gap-2">
                        <Label htmlFor="rename-project-name">{t("projects.rename.name_label")}</Label>
                        <InputGroup>
                            <InputGroupAddon align="inline-start">
                                <FolderPenIcon />
                            </InputGroupAddon>
                            <InputGroupInput id="rename-project-name" value={name} onChange={(e) => setName(e.target.value)} placeholder={t("projects.create.placeholder")} />
                        </InputGroup>
                    </div>

                    <DialogFooter>
                        <Button type="submit">{t("projects.rename.submit_button")}</Button>
                    </DialogFooter>

                </form>
            </DialogContent>
        
        </Dialog>
    )
}

export default RenameProjectForm
