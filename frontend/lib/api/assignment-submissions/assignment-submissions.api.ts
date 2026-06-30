import { baseSlice } from "../base"
import {
  AssignmentSubmissionCreateRequest,
  AssignmentSubmissionResponse,
  AssignmentSubmissionUpdateRequest,
} from "./assignment-submissions.type"

export const assignmentSubmissionsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    createSubmission: builder.mutation<
      AssignmentSubmissionResponse,
      AssignmentSubmissionCreateRequest
    >({
      query: (body) => ({
        url: "/assignment-submissions",
        method: "POST",
        body,
      }),
      invalidatesTags: (result) =>
        result
          ? [
              "AssignmentSubmission",
              {
                type: "AssignmentSubmission" as const,
                id: `ASSIGNMENT_${result.assignment_id}`,
              },
            ]
          : ["AssignmentSubmission"],
    }),

    getSubmissionById: builder.query<
      AssignmentSubmissionResponse,
      number
    >({
      query: (submissionId) => ({
        url: `/assignment-submissions/${submissionId}`,
        method: "GET",
      }),
      providesTags: (result, error, submissionId) => [
        { type: "AssignmentSubmission" as const, id: submissionId },
      ],
    }),

    getSubmissionsByAssignmentId: builder.query<
      AssignmentSubmissionResponse[],
      number
    >({
      query: (assignmentId) => ({
        url: `/assignment-submissions/assignment/${assignmentId}`,
        method: "GET",
      }),
      providesTags: (result, error, assignmentId) =>
        result
          ? [
              {
                type: "AssignmentSubmission" as const,
                id: `ASSIGNMENT_${assignmentId}`,
              },
              ...result.map(({ id }) => ({
                type: "AssignmentSubmission" as const,
                id,
              })),
            ]
          : [
              {
                type: "AssignmentSubmission" as const,
                id: `ASSIGNMENT_${assignmentId}`,
              },
            ],
    }),

    getSubmissionsByUserId: builder.query<
      AssignmentSubmissionResponse[],
      number
    >({
      query: (userId) => ({
        url: `/assignment-submissions/user/${userId}`,
        method: "GET",
      }),
      providesTags: (result, error, userId) =>
        result
          ? [
              { type: "AssignmentSubmission" as const, id: `USER_${userId}` },
              ...result.map(({ id }) => ({
                type: "AssignmentSubmission" as const,
                id,
              })),
            ]
          : [{ type: "AssignmentSubmission" as const, id: `USER_${userId}` }],
    }),

    patchSubmission: builder.mutation<
      AssignmentSubmissionResponse,
      { submissionId: number; body: AssignmentSubmissionUpdateRequest }
    >({
      query: ({ submissionId, body }) => ({
        url: `/assignment-submissions/${submissionId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result, error, { submissionId }) => [
        "AssignmentSubmission",
        { type: "AssignmentSubmission" as const, id: submissionId },
      ],
    }),

    deleteSubmission: builder.mutation<
      { message: string },
      number
    >({
      query: (submissionId) => ({
        url: `/assignment-submissions/${submissionId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, submissionId) => [
        "AssignmentSubmission",
        { type: "AssignmentSubmission" as const, id: submissionId },
      ],
    }),
  }),
})

export const {
  useCreateSubmissionMutation,
  useGetSubmissionByIdQuery,
  useGetSubmissionsByAssignmentIdQuery,
  useGetSubmissionsByUserIdQuery,
  usePatchSubmissionMutation,
  useDeleteSubmissionMutation,
} = assignmentSubmissionsApi
