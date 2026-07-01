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
      invalidatesTags: ["Assignment"],
    }),

    getAllAssignments: builder.query<AssignmentResponse[], void>({
      query: () => ({
        url: "/assignments",
        method: "GET",
      }),
      providesTags: ["Assignment"],
    }),

    getAssignmentById: builder.query<AssignmentResponse, number>({
      query: (assignmentId) => ({
        url: `/assignments/${assignmentId}`,
        method: "GET",
      }),
      providesTags: ["Assignment"],
    }),

    getAssignmentsBySessionId: builder.query<
      AssignmentResponse[],
      number
    >({
      query: (sessionId) => ({
        url: `/assignments/session/${sessionId}`,
        method: "GET",
      }),
      providesTags: ["Assignment"],
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
      invalidatesTags: ["Assignment"],
    }),

    deleteAssignment: builder.mutation<
      { message: string },
      number
    >({
      query: (assignmentId) => ({
        url: `/assignments/${assignmentId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Assignment"],
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
