import { baseSlice } from "../base"
import { FeedbackSubmissionResponse } from "../feedback-submissions/feedback-submissions.type"

export const feedbackApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    getFeedbackSubmissionsBySession: builder.query<
      FeedbackSubmissionResponse[],
      number
    >({
      query: (sessionId) => ({
        url: `/feedback/session/${sessionId}`,
        method: "GET",
      }),
      providesTags: ["Feedback"],
    }),
  }),
})

export const { useGetFeedbackSubmissionsBySessionQuery } = feedbackApi
