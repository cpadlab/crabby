import * as React from "react"
import type { Project } from "@/types/projects"
import projectsMock from "@/assets/mocks/projects.json"

export function useProjects() {
    const [projects, setProjects] = React.useState<Project[]>([])

    const sortByRecent = React.useCallback(() => {
        setProjects((prev) =>
            [...prev].sort(
                (a, b) => new Date(b.modified).getTime() - new Date(a.modified).getTime()
            )
        )
    }, [])

    const sortByOldest = React.useCallback(() => {
        setProjects((prev) =>
            [...prev].sort(
                (a, b) => new Date(a.modified).getTime() - new Date(b.modified).getTime()
            )
        )
    }, [])

    const loadProjects = React.useCallback(() => {
        const loaded = projectsMock as Project[]
        const sorted = [...loaded].sort(
            (a, b) => new Date(b.modified).getTime() - new Date(a.modified).getTime()
        )
        setProjects(sorted)
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
        sortByRecent,
        sortByOldest,
        handleCreateProject,
    }
}

export default useProjects
