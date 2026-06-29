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
          ? [
              { type: "Topic" as const, id: "LIST" },
              ...result.map(({ id }) => ({ type: "Topic" as const, id })),
            ]
          : [{ type: "Topic" as const, id: "LIST" }],
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
      invalidatesTags: [{ type: "Topic" as const, id: "LIST" }],
    }),
    updateTopic: builder.mutation<TopicResponse, { topicId: number; body: TopicUpdateRequest }>({
      query: ({ topicId, body }) => ({
        url: `/topics/${topicId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result, error, { topicId }) => [
        { type: "Topic" as const, id: "LIST" },
        { type: "Topic" as const, id: topicId },
      ],
    }),
    deleteTopic: builder.mutation<{ message: string }, number>({
      query: (topicId) => ({
        url: `/topics/${topicId}`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Topic" as const, id: "LIST" }],
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
