import { baseSlice } from "../base"
import {
  AddPersonRequest,
  ListProgramPermissionItem,
  ProgramPermissionResponse,
  UserInProgramResponse,
} from "./program-permissions.type"

export const programPermissionsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    listProgramPermissions: builder.query<
      ListProgramPermissionItem[],
      number
    >({
      query: (programId) => ({
        url: `/program-permissions/program/${programId}`,
        method: "GET",
      }),
      providesTags: (result, error, programId) =>
        result
          ? [
              { type: "ProgramPermission" as const, id: `PROGRAM_${programId}` },
              ...result.map(({ permission_id }) => ({
                type: "ProgramPermission" as const,
                id: permission_id,
              })),
            ]
          : [{ type: "ProgramPermission" as const, id: `PROGRAM_${programId}` }],
    }),

    checkUserInProgram: builder.query<
      UserInProgramResponse,
      { user_id: number; program_id: number }
    >({
      query: ({ user_id, program_id }) => ({
        url: "/program-permissions/check",
        method: "GET",
        params: { user_id, program_id },
      }),
    }),

    addPersonToProgram: builder.mutation<
      ProgramPermissionResponse,
      AddPersonRequest
    >({
      query: (body) => ({
        url: "/program-permissions",
        method: "POST",
        body,
      }),
      invalidatesTags: ["ProgramPermission"],
    }),

    removePersonFromProgram: builder.mutation<void, number>({
      query: (permissionId) => ({
        url: `/program-permissions/${permissionId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["ProgramPermission"],
    }),
  }),
})

export const {
  useListProgramPermissionsQuery,
  useCheckUserInProgramQuery,
  useAddPersonToProgramMutation,
  useRemovePersonFromProgramMutation,
} = programPermissionsApi
