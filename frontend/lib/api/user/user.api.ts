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
      providesTags: ["User"],
    }),

    getUserById: builder.query<UserResponse, number>({
      query: (id) => ({
        url: `/user/${id}`,
        method: "GET",
      }),
      providesTags: ["User"],
    }),

    getUserProgramStatus: builder.query<
      UserProgramStatusResponse,
      { userId: number; programId: number }
    >({
      query: ({ userId, programId }) => ({
        url: `/user/${userId}/program-status?program_id=${programId}`,
        method: "GET"
      }),
      providesTags: ["User"],
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
      invalidatesTags: ["User"],
    }),

    deleteUser: builder.mutation<UserResponse, number>({
      query: (id) => ({
        url: `/user/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["User"],
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
