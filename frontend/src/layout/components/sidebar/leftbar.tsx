import { Sidebar, SidebarRail } from "@/components/ui/sidebar"
import { LeftbarBody } from "./components/body/component"

export const LeftBar = () => {
    return (
        <Sidebar collapsible="icon">
            <LeftbarBody />
            <SidebarRail />
        </Sidebar>
    )
}
