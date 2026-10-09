import * as React from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { ActivityIcon, Clock3Icon, Globe2Icon, KeyRoundIcon, PlusIcon, ServerIcon, TagIcon, Trash2Icon } from "lucide-react"
import { Controller, useFieldArray, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { toast } from "@/components/ui/toast"
import { useMCPContext } from "@/context/mcp"
import type { MCPServer } from "@/types/mcp"
import { createMCPFormSchema, type MCPFormValues } from "./schema"

export interface ManageMCPFormProps {
    server?: MCPServer
    open?: boolean
    onOpenChange?: (open: boolean) => void
    trigger?: React.ReactNode
    onSuccess?: () => void
}

export function ManageMCPForm({ server, open, onOpenChange, trigger, onSuccess }: ManageMCPFormProps) {
    const { t } = useTranslation()
    const { createMCPServer, updateMCPServer, checkMCPServerByUrlResult } = useMCPContext()
    const [isSubmitting, setIsSubmitting] = React.useState(false)
    const [isTesting, setIsTesting] = React.useState(false)
    const isEdit = Boolean(server)
    const schema = React.useMemo(() => createMCPFormSchema(t), [t])

    const defaultValues = React.useMemo<MCPFormValues>(() => ({
        name: server?.name || "",
        type: server?.type || "http",
        url: server?.url || "http://localhost:8000/mcp",
        timeout: server?.timeout ?? 30,
        enabled: server?.enabled ?? true,
        headers: server?.headers.map((header) => ({
            key: header.key,
            value: "",
            configured: header.configured,
        })) || [],
    }), [server])

    const form = useForm<MCPFormValues>({ resolver: zodResolver(schema), defaultValues })
    const { fields, append, remove } = useFieldArray({ control: form.control, name: "headers" })

    React.useEffect(() => {
        if (open) form.reset(defaultValues)
    }, [open, defaultValues, form])

    const testConnection = async () => {
        const valid = await form.trigger(["type", "url", "timeout", "headers"])
        if (!valid) return
        const values = form.getValues()
        setIsTesting(true)
        try {
            const result = await checkMCPServerByUrlResult(values.url, values.headers, values.timeout, values.type)
            if (result.success && result.connected) {
                toastSuccess(t("mcp.form.test_success"))
            } else {
                toastError(result.error || t("mcp.form.test_failed"))
            }
        } finally {
            setIsTesting(false)
        }
    }

    const handleSubmit = async (values: MCPFormValues) => {
        setIsSubmitting(true)
        try {
            const payload = {
                name: values.name,
                type: values.type,
                url: values.url,
                timeout: values.timeout,
                enabled: values.enabled,
                headers: values.headers,
            }
            const result = isEdit && server
                ? await updateMCPServer(server.id, payload)
                : await createMCPServer(payload)
            if (!result.success) return
            if (!isEdit) form.reset(defaultValues)
            onSuccess?.()
            onOpenChange?.(false)
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            {trigger && <DialogTrigger render={trigger as React.ReactElement} />}
            <DialogContent className="sm:max-w-xl">
                <DialogHeader>
                    <DialogTitle>{t(isEdit ? "mcp.update.title" : "mcp.create.title")}</DialogTitle>
                </DialogHeader>

                <form onSubmit={form.handleSubmit(handleSubmit)} className="flex w-full flex-col gap-4">
                    <p className="text-sm text-muted-foreground">
                        {t(isEdit ? "mcp.update.description" : "mcp.create.description")}
                    </p>

                    <ScrollArea className="max-h-[65vh] pr-2">
                        <div className="flex flex-col gap-4 pb-1">
                            <Controller name="name" control={form.control} render={({ field, fieldState }) => (
                                <div className="flex flex-col gap-1.5" data-invalid={fieldState.invalid}>
                                    <Label htmlFor={field.name}>{t("mcp.form.name_label")}</Label>
                                    <InputGroup>
                                        <InputGroupAddon align="inline-start"><ServerIcon /></InputGroupAddon>
                                        <InputGroupInput {...field} id={field.name} disabled={isSubmitting} aria-invalid={fieldState.invalid} placeholder={t("mcp.form.name_placeholder")} autoComplete="off" />
                                    </InputGroup>
                                    {fieldState.error && <span className="text-xs text-destructive">{fieldState.error.message}</span>}
                                </div>
                            )} />

                            <Controller name="type" control={form.control} render={({ field, fieldState }) => (
                                <div className="flex flex-col gap-1.5" data-invalid={fieldState.invalid}>
                                    <Label htmlFor="manage-mcp-type">{t("mcp.form.transport_label")}</Label>
                                    <Select value={field.value} onValueChange={(value) => field.onChange(value as MCPFormValues["type"])} disabled={isSubmitting}>
                                        <SelectTrigger id="manage-mcp-type" className="w-full" aria-invalid={fieldState.invalid}>
                                            <SelectValue placeholder={t("mcp.form.transport_placeholder")} />
                                        </SelectTrigger>
                                        <SelectContent alignItemWithTrigger={false}>
                                            <SelectItem value="http">Streamable HTTP</SelectItem>
                                            <SelectItem value="sse">SSE</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <p className="text-xs text-muted-foreground">{t("mcp.form.transport_help")}</p>
                                    {fieldState.error && <span className="text-xs text-destructive">{fieldState.error.message}</span>}
                                </div>
                            )} />

                            <Controller name="url" control={form.control} render={({ field, fieldState }) => (
                                <div className="flex flex-col gap-1.5" data-invalid={fieldState.invalid}>
                                    <Label htmlFor={field.name}>{t("mcp.form.url_label")}</Label>
                                    <InputGroup>
                                        <InputGroupAddon align="inline-start"><Globe2Icon /></InputGroupAddon>
                                        <InputGroupInput {...field} id={field.name} disabled={isSubmitting} aria-invalid={fieldState.invalid} placeholder={t("mcp.form.url_placeholder")} autoComplete="url" />
                                    </InputGroup>
                                    {fieldState.error && <span className="text-xs text-destructive">{fieldState.error.message}</span>}
                                </div>
                            )} />

                            <div className="grid gap-4 sm:grid-cols-[1fr_auto] sm:items-end">
                                <Controller name="timeout" control={form.control} render={({ field, fieldState }) => (
                                    <div className="flex flex-col gap-1.5" data-invalid={fieldState.invalid}>
                                        <Label htmlFor={field.name}>{t("mcp.form.timeout_label")}</Label>
                                        <InputGroup>
                                            <InputGroupAddon align="inline-start"><Clock3Icon /></InputGroupAddon>
                                            <InputGroupInput id={field.name} type="number" step="0.5" min="0.5" max="300" value={field.value} disabled={isSubmitting} aria-invalid={fieldState.invalid} onChange={(event) => field.onChange(event.target.valueAsNumber)} />
                                        </InputGroup>
                                        {fieldState.error && <span className="text-xs text-destructive">{fieldState.error.message}</span>}
                                    </div>
                                )} />
                                <Controller name="enabled" control={form.control} render={({ field }) => (
                                    <label className="flex h-10 cursor-pointer items-center gap-2 rounded-xl border px-3 text-sm">
                                        <input type="checkbox" checked={field.value} onChange={field.onChange} disabled={isSubmitting} className="size-4 accent-primary" />
                                        <span>{t("mcp.form.enabled_label")}</span>
                                    </label>
                                )} />
                            </div>

                            <div className="flex max-w-full flex-col gap-2">
                                <div>
                                    <div className="flex items-center justify-between gap-2">
                                        <Label className="truncate">{t("mcp.form.headers_label")}</Label>
                                        <Button type="button" variant="outline" size="xs" disabled={isSubmitting} onClick={() => append({ key: "", value: "", configured: false })}>
                                            <PlusIcon />{t("mcp.form.add_header")}
                                        </Button>
                                    </div>
                                    <p className="mt-1 text-xs text-muted-foreground">{t("mcp.form.headers_help")}</p>
                                </div>
                                {fields.length === 0 && (
                                    <div className="rounded-xl border border-dashed bg-muted/20 px-3 py-4 text-center text-xs text-muted-foreground">
                                        {t("mcp.form.no_headers")}
                                    </div>
                                )}
                                {fields.map((header, index) => (
                                    <div key={header.id} className="flex items-start gap-2 rounded-2xl bg-sidebar p-2">
                                        <Controller name={`headers.${index}.key`} control={form.control} render={({ field, fieldState }) => (
                                            <div className="min-w-0 flex-1 space-y-1" data-invalid={fieldState.invalid}>
                                                <InputGroup>
                                                    <InputGroupAddon align="inline-start"><KeyRoundIcon /></InputGroupAddon>
                                                    <InputGroupInput {...field} disabled={isSubmitting} aria-invalid={fieldState.invalid} placeholder={t("mcp.form.header_key_placeholder")} autoComplete="off" />
                                                </InputGroup>
                                                {fieldState.error && <span className="text-xs text-destructive">{fieldState.error.message}</span>}
                                            </div>
                                        )} />
                                        <Controller name={`headers.${index}.value`} control={form.control} render={({ field, fieldState }) => (
                                            <div className="min-w-0 flex-1 space-y-1" data-invalid={fieldState.invalid}>
                                                <InputGroup>
                                                    <InputGroupAddon align="inline-start"><TagIcon /></InputGroupAddon>
                                                    <InputGroupInput {...field} type="password" autoComplete="new-password" disabled={isSubmitting} aria-invalid={fieldState.invalid} placeholder={header.configured ? t("mcp.form.header_keep_placeholder") : t("mcp.form.header_value_placeholder")} />
                                                </InputGroup>
                                                {fieldState.error && <span className="text-xs text-destructive">{fieldState.error.message}</span>}
                                            </div>
                                        )} />
                                        <Button type="button" variant="destructive" size="icon-sm" disabled={isSubmitting} aria-label={t("mcp.form.remove_header")} onClick={() => remove(index)}>
                                            <Trash2Icon className="size-4" />
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </ScrollArea>

                    <DialogFooter className="sm:justify-between">
                        <Button type="button" variant="outline" onClick={testConnection} disabled={isSubmitting || isTesting}>
                            <ActivityIcon className={isTesting ? "animate-pulse" : ""} />
                            {t(isTesting ? "mcp.form.testing" : "mcp.form.test_button")}
                        </Button>
                        <Button type="submit" disabled={isSubmitting || isTesting}>
                            {t(isEdit ? "mcp.update.submit_button" : "mcp.create.submit_button")}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    )
}

function toastSuccess(message: string) {
    toast.add({ type: "success", title: "MCP", description: message })
}

function toastError(message: string) {
    toast.add({ type: "error", title: "MCP", description: message })
}

export default ManageMCPForm
