import { baseSlice } from "../base"
import {
  SessionCreateRequest,
  SessionResponse,
  SessionResponseWithTopics,
  SessionUpdateRequest,
  TopicResponse,
} from "./sessions.type"

export const sessionsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    getSessions: builder.query<SessionResponse[], void>({
      query: () => ({
        url: "/sessions",
        method: "GET",
      }),
      providesTags: ["Session"],
    }),

    getSession: builder.query<SessionResponse, number>({
      query: (sessionId) => ({
        url: `/sessions/${sessionId}`,
        method: "GET",
      }),
      providesTags: ["Session"],
    }),

    getSessionsByProgramId: builder.query<
      SessionResponseWithTopics[],
      number
    >({
      query: (programId) => ({
        url: `/sessions/program/${programId}`,
        method: "GET",
      }),
      providesTags: ["Session"],
    }),

    createSession: builder.mutation<
      SessionResponse,
      SessionCreateRequest
    >({
      query: (body) => ({
        url: "/sessions",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Session"],
    }),

    updateSession: builder.mutation<
      SessionResponse,
      { sessionId: number; body: SessionUpdateRequest }
    >({
      query: ({ sessionId, body }) => ({
        url: `/sessions/${sessionId}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: ["Session"],
    }),

    deleteSession: builder.mutation<{ message: string }, number>({
      query: (sessionId) => ({
        url: `/sessions/${sessionId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Session"],
    }),

    assignTopicToSession: builder.mutation<
      SessionResponseWithTopics,
      { sessionId: number; topicId: number }
    >({
      query: ({ sessionId, topicId }) => ({
        url: `/sessions/${sessionId}/topics/${topicId}`,
        method: "POST",
      }),
      invalidatesTags: ["Session", "Topic"],
    }),

    removeTopicFromSession: builder.mutation<
      { message: string },
      { sessionId: number; topicId: number }
    >({
      query: ({ sessionId, topicId }) => ({
        url: `/sessions/${sessionId}/topics/${topicId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Session", "Topic"],
    }),

    getSessionTopics: builder.query<TopicResponse[], number>({
      query: (sessionId) => ({
        url: `/sessions/${sessionId}/topics`,
        method: "GET",
      }),
      providesTags: ["Topic"],
    }),
  }),
})

export const {
  useGetSessionsQuery,
  useGetSessionQuery,
  useGetSessionsByProgramIdQuery,
  useCreateSessionMutation,
  useUpdateSessionMutation,
  useDeleteSessionMutation,
  useAssignTopicToSessionMutation,
  useRemoveTopicFromSessionMutation,
  useGetSessionTopicsQuery,
} = sessionsApi
