export interface FeedbackSummaryRequest {
  user_id: number
  session_id: number
}

export interface FeedbackSummaryResponse {
  user_id: number
  session_id: number
  summaries: Record<string, string> // e.g. { "trainer": "...", "moderator": "..." }
}
