import * as z from "zod"

export type TFunction = (key: string) => string

export const createConnectionFormSchema = (t: TFunction) =>
    z.object({
        name: z.string().trim().min(1, t("connections.validation.name_required")).max(100),
        type: z.enum(["ollama"]),
        host: z.string().min(1, t("connections.validation.host_required")),
        timeout: z.coerce
            .number()
            .min(0.5, t("connections.validation.timeout_min"))
            .max(300, t("connections.validation.timeout_max"))
            .default(30),
        headers: z
            .array(
                z.object({
                    key: z.string().trim().min(1, t("connections.validation.header_key_required")).regex(/^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/),
                    value: z.string().max(8192),
                    configured: z.boolean().optional(),
                })
            )
            .superRefine((headers, context) => {
                const keys = new Set<string>()
                headers.forEach((header, index) => {
                    const key = header.key.toLowerCase()
                    if (!header.value && !header.configured) context.addIssue({ code: "custom", path: [index, "value"], message: t("connections.validation.header_value_required") })
                    if (keys.has(key)) context.addIssue({ code: "custom", path: [index, "key"], message: t("connections.validation.header_duplicate") })
                    keys.add(key)
                    if (["host", "content-length", "transfer-encoding", "connection"].includes(key)) context.addIssue({ code: "custom", path: [index, "key"], message: t("connections.validation.header_reserved") })
                })
            })
            .default([]),
    })

export type ConnectionFormValues = z.infer<ReturnType<typeof createConnectionFormSchema>>
