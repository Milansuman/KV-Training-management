import { baseSlice } from "../base"
import {
  CreateProgramRequest,
  ProgramProgressItem,
  ProgramResponse,
  UpdateProgramRequest,
} from "./programs.type"

export const programsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    getProgramProgress: builder.query<ProgramProgressItem[], number>({
      query: (userId) => ({
        url: `/programs/progress/${userId}`,
        method: "GET",
      }),
      providesTags: ["Program"],
    }),
    createProgram: builder.mutation<ProgramResponse, CreateProgramRequest>({
      query: (body) => ({
        url: "/programs",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Program"],
    }),
    updateProgram: builder.mutation<ProgramResponse, { programId: number; body: UpdateProgramRequest }>({
      query: ({ programId, body }) => ({
        url: `/programs/${programId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Program"],
    }),
    deleteProgram: builder.mutation<void, number>({
      query: (programId) => ({
        url: `/programs/${programId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Program"],
    }),
  }),
})

export const {
  useGetProgramProgressQuery,
  useCreateProgramMutation,
  useUpdateProgramMutation,
  useDeleteProgramMutation,
} = programsApi
