import { baseSlice } from "../base"
import { UserCreate, UserResponse, UserUpdate } from "./user.type"

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
      invalidatesTags: [{ type: "User" as const, id: "LIST" }],
    }),

    getAllUsers: builder.query<UserResponse[], void>({
      query: () => ({
        url: "/user",
        method: "GET",
      }),
      providesTags: (result) =>
        result
          ? [
              { type: "User" as const, id: "LIST" },
              ...result.map(({ id }) => ({ type: "User" as const, id })),
            ]
          : [{ type: "User" as const, id: "LIST" }],
    }),

    getUserById: builder.query<UserResponse, number>({
      query: (id) => ({
        url: `/user/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "User" as const, id }],
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
        { type: "User" as const, id: "LIST" },
        { type: "User" as const, id },
      ],
    }),

    deleteUser: builder.mutation<UserResponse, number>({
      query: (id) => ({
        url: `/user/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, id) => [
        { type: "User" as const, id: "LIST" },
        { type: "User" as const, id },
      ],
    }),
  }),
})

export const {
  useGetMyselfQuery,
  useCreateUserMutation,
  useGetAllUsersQuery,
  useGetUserByIdQuery,
  useUpdateUserMutation,
  useDeleteUserMutation,
} = userApi
