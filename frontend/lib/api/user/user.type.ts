export interface UserResponse {
  id: number
  username: string
  display_name: string
  email: string
  is_admin: boolean
}

export interface UserCreate {
  username: string
  display_name: string
  email: string
  password: string
  is_admin: boolean
}

export interface UserUpdate {
  username?: string
  display_name?: string
  email?: string
  password?: string
  is_admin?: boolean
}

export interface SessionRoleInfo {
  session_id: number
  session_title: string
  role: "TRAINER" | "MODERATOR" | "CANDIDATE" | null
}

export interface UserProgramStatusResponse {
  is_admin: boolean
  program_role: "STAFF" | "CANDIDATE" | null
  session_roles: SessionRoleInfo[]
}
