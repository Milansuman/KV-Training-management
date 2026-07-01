import { baseSlice } from "../base"
import type { FeedbackSummaryRequest, FeedbackSummaryResponse } from "./feedback.type"

export const aiFeedbackApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    getFeedbackSummary: builder.mutation<
      FeedbackSummaryResponse,
      FeedbackSummaryRequest
    >({
      query: (body) => ({
        url: "/ai/feedback/summarize",
        method: "POST",
        body,
      }),
    }),
  }),
})

export const { useGetFeedbackSummaryMutation } = aiFeedbackApi
