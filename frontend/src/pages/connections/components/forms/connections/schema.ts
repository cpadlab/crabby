import * as z from "zod"

export type TFunction = (key: string) => string

export const createConnectionFormSchema = (t: TFunction) =>
    z.object({
        name: z.string().min(1, t("connections.validation.name_required")),
        type: z.enum(["ollama"]),
        host: z.string().min(1, t("connections.validation.host_required")),
        timeout: z.coerce
            .number()
            .min(0.5, t("connections.validation.timeout_min"))
            .default(30),
        headers: z
            .array(
                z.object({
                    key: z.string().min(1, t("connections.validation.header_key_required")),
                    value: z.string().min(1, t("connections.validation.header_value_required")),
                })
            )
            .default([]),
    })

export type ConnectionFormValues = z.infer<ReturnType<typeof createConnectionFormSchema>>
