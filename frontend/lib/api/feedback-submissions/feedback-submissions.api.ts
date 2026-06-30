import { baseSlice } from "../base"
import {
  FeedbackSubmissionCreateRequest,
  FeedbackSubmissionResponse,
} from "./feedback-submissions.type"

export const feedbackSubmissionsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    createFeedbackSubmission: builder.mutation<
      FeedbackSubmissionResponse,
      FeedbackSubmissionCreateRequest
    >({
      query: (body) => ({
        url: "/feedback-submissions",
        method: "POST",
        body,
      }),
      invalidatesTags: [
        { type: "FeedbackSubmission" as const, id: "LIST" },
      ],
    }),
  }),
})

export const { useCreateFeedbackSubmissionMutation } = feedbackSubmissionsApi
