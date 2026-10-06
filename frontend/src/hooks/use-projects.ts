import * as React from "react"

export function useProjects() {
  
    const [projects] = React.useState<unknown[]>([])

    const handleCreateProject = (e: React.FormEvent) => {
        e.preventDefault()
    }

    return {
        projects,
        handleCreateProject,
    }

}

export default useProjects
