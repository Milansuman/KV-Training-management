import { baseSlice } from "../base"
import { UserCreate, UserProgramStatusResponse, UserResponse, UserUpdate } from "./user.type"

const userApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    getMyself: builder.query<UserResponse, void>({
      query: () => ({
        url: "/user/me",
      }),
      providesTags: ["User"],
    }),

    createUser: builder.mutation<UserResponse, UserCreate>({
      query: (body) => ({
        url: "/user",
        method: "POST",
        body,
      }),
      invalidatesTags: ["User"],
    }),

    getAllUsers: builder.query<UserResponse[], void>({
      query: () => ({
        url: "/user",
        method: "GET",
      }),
      providesTags: (result) =>
        result
          ? ["User", ...result.map(({ id }) => ({ type: "User" as const, id }))]
          : ["User"],
    }),

    getUserById: builder.query<UserResponse, number>({
      query: (id) => ({
        url: `/user/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "User" as const, id }],
    }),

    getUserProgramStatus: builder.query<
      UserProgramStatusResponse,
      { userId: number; programId: number }
    >({
      query: ({ userId, programId }) => ({
        url: `/user/${userId}/program-status?program_id=${programId}`,
        method: "GET"
      }),
      providesTags: (result, error, { userId, programId }) => [
        { type: "User" as const, id: `STATUS_${userId}_${programId}` },
      ],
    }),

    updateUser: builder.mutation<
      UserResponse,
      { id: number; body: UserUpdate }
    >({
      query: ({ id, body }) => ({
        url: `/user/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        "User",
        { type: "User" as const, id },
      ],
    }),

    deleteUser: builder.mutation<UserResponse, number>({
      query: (id) => ({
        url: `/user/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, id) => [
        "User",
        { type: "User" as const, id },
      ],
    }),
  }),
})

export const {
  useGetMyselfQuery,
  useGetUserProgramStatusQuery,
  useCreateUserMutation,
  useGetAllUsersQuery,
  useGetUserByIdQuery,
  useUpdateUserMutation,
  useDeleteUserMutation,
} = userApi
