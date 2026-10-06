import * as React from "react"
import type { Project } from "@/types/projects"
import projectsMock from "@/assets/mocks/projects.json"

export function useProjects() {
    const [projects, setProjects] = React.useState<Project[]>([])

    const loadProjects = React.useCallback(() => {
        setProjects(projectsMock as Project[])
    }, [])

    React.useEffect(() => {
        loadProjects()
    }, [loadProjects])

    const handleCreateProject = (name: string, e?: React.FormEvent) => {
        
        if (e) {
            e.preventDefault()
        }
        
        if (!name.trim()) return

        const newProject: Project = {
            id: `proj_${Date.now()}`,
            name: name.trim(),
            modified: new Date().toISOString(),
            chats: [],
        }

        setProjects((prev) => [newProject, ...prev])
        
    }

    return {
        projects,
        setProjects,
        loadProjects,
        handleCreateProject,
    }
}

export default useProjects
