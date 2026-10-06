import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import '@/styles.css'

import App from '@/app.tsx'
import "@/i18n"

import { Providers } from '@/components/providers'

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <Providers>
            <App />
        </Providers>
    </StrictMode>,
)
