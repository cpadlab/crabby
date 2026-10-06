import { type ComponentType, type ReactNode } from 'react';

export function ComposeProviders(...providers: ComponentType<{ children: ReactNode }>[]) {
    return function CombinedProviders({ children }: { children: ReactNode }) {
        return providers.reduceRight(
            (acc, Provider) => <Provider>{acc}</Provider>, children
        );
    };
}