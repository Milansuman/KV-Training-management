export type SessionRole = "TRAINER" | "MODERATOR" | "CANDIDATE"

export interface AddSessionPermissionRequest {
  user_id: number
  session_id: number
  role: SessionRole
}

export interface UpdateSessionPermissionRequest {
  role: SessionRole
}

export interface SessionPermissionResponse {
  id: number
  user_id: number
  session_id: number
  role: SessionRole
}

export interface SessionResponse {
  id: number
  title: string
  description: string
  start_datetime: string
  end_datetime: string
  program_id: number
  created_at: string
  updated_at: string
}

export interface SessionWithRoleResponse extends SessionResponse {
  role: SessionRole | null
}

export interface SessionUserResponse {
  id: number
  user_id: number
  session_id: number
  role: SessionRole
  display_name: string
  email: string
}
