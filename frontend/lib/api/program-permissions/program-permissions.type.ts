export type ProgramRole = "STAFF" | "CANDIDATE"

export interface AddPersonRequest {
  user_id: number
  program_id: number
  role: ProgramRole
}

export interface ProgramPermissionResponse {
  id: number
  user_id: number
  program_id: number
  role: ProgramRole
}

export interface UserInProgramResponse {
  is_member: boolean
}

export interface UpdatePersonRequest {
  role: ProgramRole
}

export interface ListProgramPermissionItem {
  permission_id: number
  user_id: number
  username: string
  display_name: string
  role: ProgramRole
}
