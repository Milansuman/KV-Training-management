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
      invalidatesTags: ["AssignmentSubmission"],
    }),

    getSubmissionById: builder.query<
      AssignmentSubmissionResponse,
      number
    >({
      query: (submissionId) => ({
        url: `/assignment-submissions/${submissionId}`,
        method: "GET",
      }),
      providesTags: ["AssignmentSubmission"],
    }),

    getSubmissionsByAssignmentId: builder.query<
      AssignmentSubmissionResponse[],
      number
    >({
      query: (assignmentId) => ({
        url: `/assignment-submissions/assignment/${assignmentId}`,
        method: "GET",
      }),
      providesTags: ["AssignmentSubmission"],
    }),

    getSubmissionsByUserId: builder.query<
      AssignmentSubmissionResponse[],
      number
    >({
      query: (userId) => ({
        url: `/assignment-submissions/user/${userId}`,
        method: "GET",
      }),
      providesTags: ["AssignmentSubmission"],
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
      invalidatesTags: ["AssignmentSubmission"],
    }),

    deleteSubmission: builder.mutation<
      { message: string },
      number
    >({
      query: (submissionId) => ({
        url: `/assignment-submissions/${submissionId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["AssignmentSubmission"],
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
