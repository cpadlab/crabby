import * as React from "react"
import type { Project } from "@/types/projects"

export function useProjects() {
    
    const [projects, setProjects] = React.useState<Project[]>([])

    const handleCreateProject = (e: React.FormEvent) => {
        e.preventDefault()
    }

    return {
        projects,
        setProjects,
        handleCreateProject,
    }
}

export default useProjects
