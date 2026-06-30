export interface FeedbackSubmissionCreateRequest {
  user_id: number
  recipient_id: number | null
  feedback_id: number
  text: string
}

export interface FeedbackSubmissionResponse {
  id: number
  user_id: number
  recipient_id: number | null
  feedback_id: number
  text: string
  submitted_at: string
}
