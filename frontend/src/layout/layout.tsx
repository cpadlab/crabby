import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar'
import { Outlet } from 'react-router-dom'
import { LeftBar } from './components/sidebar/leftbar'

const Layout = () => {
    return (
        <SidebarProvider>
            <LeftBar />
            <SidebarInset>
                <Outlet />
            </SidebarInset>
        </SidebarProvider>
    )
}

export default Layout