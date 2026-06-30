import { baseSlice } from "../base"
import {
  AddSessionPermissionRequest,
  SessionPermissionResponse,
  SessionResponse,
  SessionUserResponse,
  SessionWithRoleResponse,
  UpdateSessionPermissionRequest,
} from "./session-permissions.type"

export const sessionPermissionsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    getSessionsByProgram: builder.query<SessionResponse[], number>({
      query: (programId) => ({
        url: `/session-permissions/program/${programId}`,
        method: "GET",
      }),
      providesTags: (result, error, programId) =>
        result
          ? [
              { type: "SessionPermission" as const, id: `PROGRAM_${programId}` },
              ...result.map(({ id }) => ({
                type: "SessionPermission" as const,
                id,
              })),
            ]
          : [{ type: "SessionPermission" as const, id: `PROGRAM_${programId}` }],
    }),

    getSessionsWithRole: builder.query<
      SessionWithRoleResponse[],
      { programId: number; userId: number }
    >({
      query: ({ programId, userId }) => ({
        url: `/session-permissions/program/${programId}/user/${userId}`,
        method: "GET",
      }),
      providesTags: (result, error, { programId, userId }) =>
        result
          ? [
              {
                type: "SessionPermission" as const,
                id: `PROGRAM_${programId}_USER_${userId}`,
              },
              ...result.map(({ id }) => ({
                type: "SessionPermission" as const,
                id,
              })),
            ]
          : [
              {
                type: "SessionPermission" as const,
                id: `PROGRAM_${programId}_USER_${userId}`,
              },
            ],
    }),

    addSessionPermission: builder.mutation<
      SessionPermissionResponse,
      AddSessionPermissionRequest
    >({
      query: (body) => ({
        url: "/session-permissions",
        method: "POST",
        body,
      }),
      invalidatesTags: ["SessionPermission"],
    }),

    updateSessionPermission: builder.mutation<
      SessionPermissionResponse,
      { permissionId: number; body: UpdateSessionPermissionRequest }
    >({
      query: ({ permissionId, body }) => ({
        url: `/session-permissions/${permissionId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result, error, { permissionId }) => [
        "SessionPermission",
        { type: "SessionPermission" as const, id: permissionId },
      ],
    }),

    getSessionUsers: builder.query<SessionUserResponse[], number>({
      query: (sessionId) => ({
        url: `/session-permissions/session/${sessionId}`,
        method: "GET",
      }),
      providesTags: (result, error, sessionId) =>
        result
          ? [
              { type: "SessionPermission" as const, id: `SESSION_${sessionId}` },
              ...result.map(({ id }) => ({
                type: "SessionPermission" as const,
                id,
              })),
            ]
          : [{ type: "SessionPermission" as const, id: `SESSION_${sessionId}` }],
    }),

    deleteSessionPermission: builder.mutation<void, number>({
      query: (permissionId) => ({
        url: `/session-permissions/${permissionId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, permissionId) => [
        "SessionPermission",
        { type: "SessionPermission" as const, id: permissionId },
      ],
    }),
  }),
})

export const {
  useGetSessionsByProgramQuery,
  useGetSessionsWithRoleQuery,
  useGetSessionUsersQuery,
  useAddSessionPermissionMutation,
  useUpdateSessionPermissionMutation,
  useDeleteSessionPermissionMutation,
} = sessionPermissionsApi
