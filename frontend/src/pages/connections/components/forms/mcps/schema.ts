import * as z from "zod"

type TFunction = (key: string) => string

const headerKey = /^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/
const reservedHeaders = ["host", "content-length", "transfer-encoding", "connection"]

export const createMCPFormSchema = (t: TFunction) => z.object({
    name: z.string().trim().min(1, t("mcp.validation.name_required")).max(120),
    type: z.enum(["http", "sse"]),
    url: z.string().trim().min(1, t("mcp.validation.url_required")).max(2048).url(t("mcp.validation.url_invalid")),
    timeout: z.coerce.number()
        .min(0.5, t("mcp.validation.timeout_min"))
        .max(300, t("mcp.validation.timeout_max")),
    enabled: z.boolean(),
    headers: z.array(z.object({
        key: z.string().trim().min(1, t("mcp.validation.header_key_required")).max(256).regex(headerKey, t("mcp.validation.header_key_invalid")),
        value: z.string().max(8192).refine((value) => !/[\r\n\0]/.test(value), t("mcp.validation.header_value_invalid")),
        configured: z.boolean().optional(),
    })).max(100).superRefine((headers, context) => {
        const keys = new Set<string>()
        headers.forEach((header, index) => {
            const key = header.key.toLowerCase()
            if (keys.has(key)) {
                context.addIssue({ code: "custom", path: [index, "key"], message: t("mcp.validation.header_duplicate") })
            }
            if (reservedHeaders.includes(key)) {
                context.addIssue({ code: "custom", path: [index, "key"], message: t("mcp.validation.header_reserved") })
            }
            if (!header.value && !header.configured) {
                context.addIssue({ code: "custom", path: [index, "value"], message: t("mcp.validation.header_value_required") })
            }
            keys.add(key)
        })
    }),
})

export type MCPFormValues = z.infer<ReturnType<typeof createMCPFormSchema>>
