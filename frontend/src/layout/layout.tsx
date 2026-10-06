import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar'
import { Outlet } from 'react-router-dom'
import { LeftBar } from './components/sidebar/leftbar'
import { Toaster } from '@/components/ui/toast'

const Layout = () => {
    return (
        <SidebarProvider>
            <LeftBar />
            <SidebarInset>
                <Outlet />
            </SidebarInset>
            <Toaster />
        </SidebarProvider>
    )
}

export default Layout