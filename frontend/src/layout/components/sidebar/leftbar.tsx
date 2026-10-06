import { Sidebar, SidebarRail } from "@/components/ui/sidebar"
import { LeftbarBody } from "./components/body"

export const LeftBar = () => {
    return (
        <Sidebar collapsible="icon">
            <LeftbarBody />
            <SidebarRail />
        </Sidebar>
    )
}
