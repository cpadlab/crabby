import { Skeleton } from "@/components/ui/skeleton"

export function ConnectionsSkeleton() {
    return (
        <div className="flex flex-col gap-4">
            {[1, 2].map((i) => (
                <div key={i} className="bg-card border rounded-4xl p-4 flex flex-col gap-3">
                    <div className="flex items-center justify-between gap-4">
                        <div className="flex items-center gap-3 flex-1">
                            <Skeleton className="w-[38px] h-[38px] rounded-2xl shrink-0" />
                            <div className="flex flex-col gap-2 flex-1">
                                <Skeleton className="h-5 w-1/3 rounded-md" />
                                <Skeleton className="h-4 w-1/2 rounded-md" />
                            </div>
                        </div>
                        <Skeleton className="w-8 h-8 rounded-full shrink-0" />
                    </div>
                    <div className="pt-3 border-t flex items-center justify-between">
                        <Skeleton className="h-4 w-40 rounded-md" />
                        <Skeleton className="h-6 w-24 rounded-lg" />
                    </div>
                </div>
            ))}
        </div>
    )
}

export default ConnectionsSkeleton

