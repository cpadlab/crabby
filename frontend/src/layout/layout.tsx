import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar'
import { Outlet } from 'react-router-dom'
import { LeftBar } from './components/sidebar/leftbar'
import { Toaster } from '@/components/ui/toast'
import { ScrollArea } from '@/components/ui/scroll-area'

const Layout = () => {
    return (
        <SidebarProvider>
            <LeftBar />
            <SidebarInset>
                <ScrollArea className="h-dvh">
                    <Outlet />
                </ScrollArea>
            </SidebarInset>
            <Toaster />
        </SidebarProvider>
    )
}

export default Layout