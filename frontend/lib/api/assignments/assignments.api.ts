import { baseSlice } from "../base"
import {
  AssignmentCreateRequest,
  AssignmentResponse,
  AssignmentUpdateRequest,
} from "./assignments.type"

export const assignmentsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    createAssignment: builder.mutation<
      AssignmentResponse,
      AssignmentCreateRequest
    >({
      query: (body) => ({
        url: "/assignments",
        method: "POST",
        body,
      }),
      invalidatesTags: (result) =>
        result
          ? [
              { type: "Assignment" as const, id: "LIST" },
              {
                type: "Assignment" as const,
                id: `SESSION_${result.session_id}`,
              },
            ]
          : [{ type: "Assignment" as const, id: "LIST" }],
    }),

    getAllAssignments: builder.query<AssignmentResponse[], void>({
      query: () => ({
        url: "/assignments",
        method: "GET",
      }),
      providesTags: (result) =>
        result
          ? [
              { type: "Assignment" as const, id: "LIST" },
              ...result.map(({ id }) => ({
                type: "Assignment" as const,
                id,
              })),
            ]
          : [{ type: "Assignment" as const, id: "LIST" }],
    }),

    getAssignmentById: builder.query<AssignmentResponse, number>({
      query: (assignmentId) => ({
        url: `/assignments/${assignmentId}`,
        method: "GET",
      }),
      providesTags: (result, error, assignmentId) => [
        { type: "Assignment" as const, id: assignmentId },
      ],
    }),

    getAssignmentsBySessionId: builder.query<
      AssignmentResponse[],
      number
    >({
      query: (sessionId) => ({
        url: `/assignments/session/${sessionId}`,
        method: "GET",
      }),
      providesTags: (result, error, sessionId) =>
        result
          ? [
              {
                type: "Assignment" as const,
                id: `SESSION_${sessionId}`,
              },
              ...result.map(({ id }) => ({
                type: "Assignment" as const,
                id,
              })),
            ]
          : [{ type: "Assignment" as const, id: `SESSION_${sessionId}` }],
    }),

    patchAssignment: builder.mutation<
      AssignmentResponse,
      { assignmentId: number; body: AssignmentUpdateRequest }
    >({
      query: ({ assignmentId, body }) => ({
        url: `/assignments/${assignmentId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result, error, { assignmentId }) => [
        { type: "Assignment" as const, id: "LIST" },
        { type: "Assignment" as const, id: assignmentId },
      ],
    }),

    deleteAssignment: builder.mutation<
      { message: string },
      number
    >({
      query: (assignmentId) => ({
        url: `/assignments/${assignmentId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, assignmentId) => [
        { type: "Assignment" as const, id: "LIST" },
        { type: "Assignment" as const, id: assignmentId },
      ],
    }),
  }),
})

export const {
  useCreateAssignmentMutation,
  useGetAllAssignmentsQuery,
  useGetAssignmentByIdQuery,
  useGetAssignmentsBySessionIdQuery,
  usePatchAssignmentMutation,
  useDeleteAssignmentMutation,
} = assignmentsApi
