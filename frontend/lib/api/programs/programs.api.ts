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
      providesTags: (result) =>
        result
          ? [
              { type: "Program" as const, id: "LIST" },
              ...result.map(({ id }) => ({ type: "Program" as const, id })),
            ]
          : [{ type: "Program" as const, id: "LIST" }],
    }),
    createProgram: builder.mutation<ProgramResponse, CreateProgramRequest>({
      query: (body) => ({
        url: "/programs",
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Program" as const, id: "LIST" }],
    }),
    updateProgram: builder.mutation<ProgramResponse, { programId: number; body: UpdateProgramRequest }>({
      query: ({ programId, body }) => ({
        url: `/programs/${programId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result, error, { programId }) => [
        { type: "Program" as const, id: "LIST" },
        { type: "Program" as const, id: programId },
      ],
    }),
    deleteProgram: builder.mutation<void, number>({
      query: (programId) => ({
        url: `/programs/${programId}`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Program" as const, id: "LIST" }],
    }),
  }),
})

export const {
  useGetProgramProgressQuery,
  useCreateProgramMutation,
  useUpdateProgramMutation,
  useDeleteProgramMutation,
} = programsApi
