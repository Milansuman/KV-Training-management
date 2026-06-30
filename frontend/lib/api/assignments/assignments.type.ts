export interface AssignmentCreateRequest {
  title: string
  description: string
  session_id: number
  due_at: string // ISO datetime
}

export interface AssignmentUpdateRequest {
  title?: string
  description?: string
  due_at?: string // ISO datetime
}

export interface AssignmentResponse {
  id: number
  title: string
  description: string
  session_id: number
  due_at: string
  created_at: string
  updated_at: string
}
