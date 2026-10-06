import * as React from "react"
import { useTranslation } from "react-i18next"
import { FolderPenIcon, LightbulbIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group"
import { Label } from "@/components/ui/label"
import { useProjects } from "@/hooks/use-projects"

export interface CreateProjectFormProps {
    open?: boolean
    onOpenChange?: (open: boolean) => void
    trigger?: React.ReactNode
}

export function CreateProjectForm({ open, onOpenChange, trigger }: CreateProjectFormProps) {
    
    const { t } = useTranslation()
    const [name, setName] = React.useState("")
    const { handleCreateProject } = useProjects()

    const handleSubmit = (e: React.FormEvent) => {
        handleCreateProject(name, e)
        setName("")
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
                    <DialogTitle>{t("projects.create.title")}</DialogTitle>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                    <div className="flex flex-col gap-2">
                        <Label htmlFor="project-name">{t("projects.create.name_label")}</Label>
                        <InputGroup>
                            <InputGroupAddon align="inline-start">
                                <FolderPenIcon />
                            </InputGroupAddon>
                            <InputGroupInput id="project-name" value={name} onChange={(e) => setName(e.target.value)} placeholder={t("projects.create.placeholder")} />
                        </InputGroup>
                    </div>

                    <div className="rounded-4xl bg-muted p-4 text-xs flex text-muted-foreground gap-4 items-center">
                        <LightbulbIcon className="min-w-4 w-4 min-h-4 h-4" />
                        <p>{t("projects.create.description")}</p>
                    </div>

                    <DialogFooter>
                        <Button type="submit">{t("projects.create.submit_button")}</Button>
                    </DialogFooter>

                </form>
            </DialogContent>
        
        </Dialog>
    )
}

export default CreateProjectForm
