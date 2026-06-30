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
      providesTags: (result) =>
        result
          ? ["Session", ...result.map(({ id }) => ({ type: "Session" as const, id }))]
          : ["Session"],
    }),

    getSession: builder.query<SessionResponse, number>({
      query: (sessionId) => ({
        url: `/sessions/${sessionId}`,
        method: "GET",
      }),
      providesTags: (result, error, sessionId) => [
        { type: "Session" as const, id: sessionId },
      ],
    }),

    getSessionsByProgramId: builder.query<
      SessionResponseWithTopics[],
      number
    >({
      query: (programId) => ({
        url: `/sessions/program/${programId}`,
        method: "GET",
      }),
      providesTags: (result, error, programId) =>
        result
          ? [
              { type: "Session" as const, id: `PROGRAM_${programId}` },
              ...result.map(({ id }) => ({ type: "Session" as const, id })),
            ]
          : [{ type: "Session" as const, id: `PROGRAM_${programId}` }],
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
      invalidatesTags: (result) =>
        result
          ? [
              "Session",
              {
                type: "Session" as const,
                id: `PROGRAM_${result.program_id}`,
              },
              { type: "Program" as const, id: result.program_id },
              "Program",
            ]
          : ["Session"],
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
      invalidatesTags: (result, error, { sessionId }) =>
        result
          ? [
              "Session",
              { type: "Session" as const, id: sessionId },
              {
                type: "Session" as const,
                id: `PROGRAM_${result.program_id}`,
              },
            ]
          : ["Session", { type: "Session" as const, id: sessionId }],
    }),

    deleteSession: builder.mutation<{ message: string }, number>({
      query: (sessionId) => ({
        url: `/sessions/${sessionId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, sessionId) => [
        "Session",
        { type: "Session" as const, id: sessionId },
        "Program",
      ],
    }),

    assignTopicToSession: builder.mutation<
      SessionResponseWithTopics,
      { sessionId: number; topicId: number }
    >({
      query: ({ sessionId, topicId }) => ({
        url: `/sessions/${sessionId}/topics/${topicId}`,
        method: "POST",
      }),
      invalidatesTags: (result, error, { sessionId }) => [
        { type: "Session" as const, id: sessionId },
        "Session",
        "Topic",
      ],
    }),

    removeTopicFromSession: builder.mutation<
      { message: string },
      { sessionId: number; topicId: number }
    >({
      query: ({ sessionId, topicId }) => ({
        url: `/sessions/${sessionId}/topics/${topicId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, { sessionId }) => [
        { type: "Session" as const, id: sessionId },
        "Session",
        "Topic",
      ],
    }),

    getSessionTopics: builder.query<TopicResponse[], number>({
      query: (sessionId) => ({
        url: `/sessions/${sessionId}/topics`,
        method: "GET",
      }),
      providesTags: (result, error, sessionId) =>
        result
          ? [
              { type: "Topic" as const, id: sessionId },
              ...result.map(({ id }) => ({ type: "Topic" as const, id })),
            ]
          : [{ type: "Topic" as const, id: sessionId }],
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
