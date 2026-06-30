import { baseSlice } from "../base";
import { UserResponse } from "./user.type";

const userApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    getMyself: builder.query<UserResponse, void>({
      query: () => ({
        url: "/user/me"
      }),
      providesTags: ["User"]
    })
  })
});

export const {
  useGetMyselfQuery
} = userApi
