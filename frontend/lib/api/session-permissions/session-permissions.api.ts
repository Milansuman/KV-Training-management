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
      providesTags: ["SessionPermission"],
    }),

    getSessionsWithRole: builder.query<
      SessionWithRoleResponse[],
      { programId: number; userId: number }
    >({
      query: ({ programId, userId }) => ({
        url: `/session-permissions/program/${programId}/user/${userId}`,
        method: "GET",
      }),
      providesTags: ["SessionPermission"],
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
      invalidatesTags: ["SessionPermission"],
    }),

    getSessionUsers: builder.query<SessionUserResponse[], number>({
      query: (sessionId) => ({
        url: `/session-permissions/session/${sessionId}`,
        method: "GET",
      }),
      providesTags: ["SessionPermission"],
    }),

    deleteSessionPermission: builder.mutation<void, number>({
      query: (permissionId) => ({
        url: `/session-permissions/${permissionId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["SessionPermission"],
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
