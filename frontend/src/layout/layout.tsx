import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Outlet } from 'react-router-dom'
import { LeftBar } from './components/sidebar/leftbar'

const Layout = () => {
    return (
        <SidebarProvider>
            <LeftBar />
            <SidebarInset>
                <SidebarTrigger />
                <Outlet />
            </SidebarInset>
        </SidebarProvider>
    )
}

export default Layout