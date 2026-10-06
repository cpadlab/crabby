import { Route, Routes } from "react-router-dom"

import Layout from "@/layout/layout"
import HomePage from "@/pages/home/page"
import ConnectionsPage from "./pages/connections/page"

function App() {
    return (
        <Routes>
            <Route path="/" element={<Layout />} >
                <Route index element={<HomePage />} />
                <Route path="connections" element={<ConnectionsPage />} />
            </Route>
        </Routes>
    )
}

export default App
