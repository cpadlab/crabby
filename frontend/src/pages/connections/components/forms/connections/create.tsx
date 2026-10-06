import * as React from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { ClockIcon, GlobeIcon, KeyIcon, PlusIcon, ServerIcon, TagIcon, Trash2Icon } from "lucide-react"
import { Controller, useFieldArray, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useConnectionsContext } from "@/context/connections"
import { createConnectionFormSchema, type ConnectionFormValues } from "./schema"

export interface CreateConnectionFormProps {
    open?: boolean
    onOpenChange?: (open: boolean) => void
    trigger?: React.ReactNode
    onSuccess?: () => void
}

export function CreateConnectionForm({ open, onOpenChange, trigger, onSuccess }: CreateConnectionFormProps) {
    
    const { t } = useTranslation()
    const { createConnection } = useConnectionsContext()
    const [isSubmitting, setIsSubmitting] = React.useState(false)

    const schema = React.useMemo(() => createConnectionFormSchema(t), [t])

    const form = useForm<ConnectionFormValues>({
        resolver: zodResolver(schema),
        defaultValues: {
            name: "",
            type: "ollama",
            host: "http://localhost:11434",
            timeout: 30,
            headers: [],
        },
    })

    const { fields, append, remove } = useFieldArray({
        control: form.control,
        name: "headers",
    })

    const handleSubmit = async (values: ConnectionFormValues) => {
        setIsSubmitting(true)
        try {
            const res = await createConnection({
                name: values.name,
                type: values.type,
                host: values.host,
                timeout: values.timeout,
                headers: values.headers,
            })

            if (res.success) {
                form.reset()
                onSuccess?.()
                onOpenChange?.(false)
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            
            {trigger && <DialogTrigger render={trigger as React.ReactElement} />}

            <DialogContent>
                
                <DialogHeader>
                    <DialogTitle>{t("connections.create.title")}</DialogTitle>
                </DialogHeader>

                <form onSubmit={form.handleSubmit(handleSubmit)} className="flex flex-col gap-4">
                    
                    <p className="text-sm text-muted-foreground">{t("connections.create.description")}</p>

                    <ScrollArea className="max-h-[60vh] pr-3">
                        <div className="flex flex-col gap-4 p-1">
                            
                            <Controller name="name" control={form.control}
                                render={({ field, fieldState }) => (
                                    <div className="flex flex-col gap-2" data-invalid={fieldState.invalid}>
                                        <Label htmlFor={field.name}>{t("connections.form.name_label")}</Label>
                                        <InputGroup>
                                            <InputGroupAddon align="inline-start">
                                                <ServerIcon />
                                            </InputGroupAddon>
                                            <InputGroupInput {...field} id={field.name} disabled={isSubmitting} aria-invalid={fieldState.invalid} placeholder={t("connections.form.name_placeholder")} autoComplete="off" />
                                        </InputGroup>
                                        {fieldState.invalid && (
                                            <span className="text-xs text-destructive">{fieldState.error?.message}</span>
                                        )}
                                    </div>
                                )}
                            />

                            <Controller name="type" control={form.control}
                                render={({ field, fieldState }) => (
                                    <div className="flex flex-col gap-2" data-invalid={fieldState.invalid}>
                                        <Label htmlFor="create-connection-type">{t("connections.form.type_label")}</Label>
                                        <Select name={field.name} value={field.value} onValueChange={(val) => field.onChange(val as "ollama")} disabled={isSubmitting}>
                                            <SelectTrigger id="create-connection-type" aria-invalid={fieldState.invalid} className="w-full">
                                                <SelectValue placeholder={t("connections.form.type_placeholder")} />
                                            </SelectTrigger>
                                            <SelectContent alignItemWithTrigger={false}>
                                                <SelectItem value="ollama">Ollama</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        {fieldState.invalid && (
                                            <span className="text-xs text-destructive">{fieldState.error?.message}</span>
                                        )}
                                    </div>
                                )}
                            />

                            <Controller name="host" control={form.control}
                                render={({ field, fieldState }) => (
                                    <div className="flex flex-col gap-2" data-invalid={fieldState.invalid}>
                                        <Label htmlFor={field.name}>{t("connections.form.host_label")}</Label>
                                        <InputGroup>
                                            <InputGroupAddon align="inline-start">
                                                <GlobeIcon />
                                            </InputGroupAddon>
                                            <InputGroupInput {...field} id={field.name} disabled={isSubmitting} aria-invalid={fieldState.invalid} placeholder={t("connections.form.host_placeholder")} autoComplete="off" />
                                        </InputGroup>
                                        {fieldState.invalid && (
                                            <span className="text-xs text-destructive">{fieldState.error?.message}</span>
                                        )}
                                    </div>
                                )}
                            />

                            <Controller name="timeout" control={form.control}
                                render={({ field, fieldState }) => (
                                    <div className="flex flex-col gap-1.5" data-invalid={fieldState.invalid}>
                                        <Label htmlFor={field.name}>{t("connections.form.timeout_label")}</Label>
                                        <InputGroup>
                                            <InputGroupAddon align="inline-start">
                                                <ClockIcon />
                                            </InputGroupAddon>
                                            <InputGroupInput {...field} id={field.name} type="number" step="0.5" disabled={isSubmitting} aria-invalid={fieldState.invalid} placeholder={t("connections.form.timeout_placeholder")} onChange={(e) => {const val = e.target.valueAsNumber;field.onChange(Number.isNaN(val) ? e.target.value : val)}} />
                                        </InputGroup>
                                        {fieldState.invalid && (
                                            <span className="text-xs text-destructive">{fieldState.error?.message}</span>
                                        )}
                                    </div>
                                )}
                            />

                            <div className="flex flex-col gap-2">
                                
                                <div className="flex gap-2 items-center justify-between">
                                    <Label className="truncate">{t("connections.form.headers_label")}</Label>
                                    <Button type="button" variant="outline" size="xs" disabled={isSubmitting} onClick={() => append({ key: "", value: "" })}>
                                        <PlusIcon />
                                        <span>{t("connections.form.add_header_button")}</span>
                                    </Button>
                                </div>

                                {fields.map((headerField, index) => (
                                    <div key={headerField.id} className="flex items-start gap-2">
                                        
                                        <Controller name={`headers.${index}.key`} control={form.control}
                                            render={({ field, fieldState }) => (
                                                <div className="flex-1 flex flex-col gap-1" data-invalid={fieldState.invalid}>
                                                    <InputGroup>
                                                        <InputGroupAddon align="inline-start">
                                                            <KeyIcon />
                                                        </InputGroupAddon>
                                                        <InputGroupInput {...field} disabled={isSubmitting} aria-invalid={fieldState.invalid} placeholder={t("connections.form.header_key_placeholder")} />
                                                    </InputGroup>
                                                    {fieldState.invalid && (
                                                        <span className="text-xs text-destructive">{fieldState.error?.message}</span>
                                                    )}
                                                </div>
                                            )}
                                        />

                                        <Controller
                                            name={`headers.${index}.value`}
                                            control={form.control}
                                            render={({ field, fieldState }) => (
                                                <div className="flex-1 flex flex-col gap-1" data-invalid={fieldState.invalid}>
                                                    <InputGroup>
                                                        <InputGroupAddon align="inline-start">
                                                            <TagIcon />
                                                        </InputGroupAddon>
                                                        <InputGroupInput {...field} disabled={isSubmitting} aria-invalid={fieldState.invalid} placeholder={t("connections.form.header_value_placeholder")}/>
                                                    </InputGroup>
                                                    {fieldState.invalid && (
                                                        <span className="text-xs text-destructive">{fieldState.error?.message}</span>
                                                    )}
                                                </div>
                                            )}
                                        />

                                        <Button type="button" variant="ghost" size="icon-sm" disabled={isSubmitting} onClick={() => remove(index)} className="mt-0.5 text-muted-foreground hover:text-destructive">
                                            <Trash2Icon className="w-4 h-4" />
                                        </Button>

                                    </div>
                                ))}
                            </div>

                        </div>
                    </ScrollArea>

                    <DialogFooter>
                        <Button type="submit" disabled={isSubmitting}>
                            {t("connections.create.submit_button")}
                        </Button>
                    </DialogFooter>

                </form>
                
            </DialogContent>
        </Dialog>
    )
}

export default CreateConnectionForm
