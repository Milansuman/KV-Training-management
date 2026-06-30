import { baseSlice } from "../base"
import {
  TopicCreateRequest,
  TopicResponse,
  TopicUpdateRequest,
} from "./topics.type"

export const topicsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    getTopics: builder.query<TopicResponse[], void>({
      query: () => ({
        url: "/topics",
        method: "GET",
      }),
      providesTags: (result) =>
        result
          ? ["Topic", ...result.map(({ id }) => ({ type: "Topic" as const, id }))]
          : ["Topic"],
    }),
    getTopic: builder.query<TopicResponse, number>({
      query: (topicId) => ({
        url: `/topics/${topicId}`,
        method: "GET",
      }),
      providesTags: (result, error, topicId) => [{ type: "Topic" as const, id: topicId }],
    }),
    createTopic: builder.mutation<TopicResponse, TopicCreateRequest>({
      query: (body) => ({
        url: "/topics",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Topic"],
    }),
    updateTopic: builder.mutation<TopicResponse, { topicId: number; body: TopicUpdateRequest }>({
      query: ({ topicId, body }) => ({
        url: `/topics/${topicId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result, error, { topicId }) => [
        "Topic",
        { type: "Topic" as const, id: topicId },
      ],
    }),
    deleteTopic: builder.mutation<{ message: string }, number>({
      query: (topicId) => ({
        url: `/topics/${topicId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Topic"],
    }),
  }),
})

export const {
  useGetTopicsQuery,
  useGetTopicQuery,
  useCreateTopicMutation,
  useUpdateTopicMutation,
  useDeleteTopicMutation,
} = topicsApi
