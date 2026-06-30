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
      providesTags: (result, error, sessionId) =>
        result
          ? [
              { type: "Feedback" as const, id: sessionId },
              ...result.map(({ id }) => ({
                type: "Feedback" as const,
                id,
              })),
            ]
          : [{ type: "Feedback" as const, id: sessionId }],
    }),
  }),
})

export const { useGetFeedbackSubmissionsBySessionQuery } = feedbackApi
