import { baseSlice } from "../base"
import {
  SessionCreateRequest,
  SessionResponse,
  SessionUpdateRequest,
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
          ? [
              { type: "Session" as const, id: "LIST" },
              ...result.map(({ id }) => ({ type: "Session" as const, id })),
            ]
          : [{ type: "Session" as const, id: "LIST" }],
    }),
    getSession: builder.query<SessionResponse, number>({
      query: (sessionId) => ({
        url: `/sessions/${sessionId}`,
        method: "GET",
      }),
      providesTags: (result, error, sessionId) => [{ type: "Session" as const, id: sessionId }],
    }),
    getSessionsByProgramId: builder.query<SessionResponse[], number>({
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
    createSession: builder.mutation<SessionResponse, SessionCreateRequest>({
      query: (body) => ({
        url: "/sessions",
        method: "POST",
        body,
      }),
      invalidatesTags: (result) =>
        result
          ? [
              { type: "Session" as const, id: "LIST" },
              { type: "Session" as const, id: `PROGRAM_${result.program_id}` },
              { type: "Program" as const, id: result.program_id },
              { type: "Program" as const, id: "LIST" },
            ]
          : [{ type: "Session" as const, id: "LIST" }],
    }),
    updateSession: builder.mutation<SessionResponse, { sessionId: number; body: SessionUpdateRequest }>({
      query: ({ sessionId, body }) => ({
        url: `/sessions/${sessionId}`,
        method: "PUT",
      }),
      invalidatesTags: (result, error, { sessionId }) =>
        result
          ? [
              { type: "Session" as const, id: "LIST" },
              { type: "Session" as const, id: sessionId },
              { type: "Session" as const, id: `PROGRAM_${result.program_id}` },
            ]
          : [
              { type: "Session" as const, id: "LIST" },
              { type: "Session" as const, id: sessionId },
            ],
    }),
    deleteSession: builder.mutation<{ message: string }, number>({
      query: (sessionId) => ({
        url: `/sessions/${sessionId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, sessionId) => [
        { type: "Session" as const, id: "LIST" },
        { type: "Session" as const, id: sessionId },
        { type: "Program" as const, id: "LIST" },
      ],
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
} = sessionsApi
