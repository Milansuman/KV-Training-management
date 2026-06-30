export interface AssignmentSubmissionCreateRequest {
  url: string
  user_id: number
  assignment_id: number
}

export interface AssignmentSubmissionUpdateRequest {
  url?: string
}

export interface AssignmentSubmissionResponse {
  id: number
  url: string
  user_id: number
  assignment_id: number
  created_at: string
  updated_at: string
}
