import { baseSlice } from "../base"
import {
  GoogleHandshakeRequest,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserResponse,
} from "./auth.type"

export const authApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    register: builder.mutation<UserResponse, RegisterRequest>({
      query: (body) => ({
        url: "/auth/register",
        method: "POST",
        body,
      }),
    }),
    login: builder.mutation<TokenResponse, LoginRequest>({
      query: (body) => ({
        url: "/auth/login",
        method: "POST",
        body,
      }),
    }),
    refresh: builder.mutation<TokenResponse, void>({
      query: () => ({
        url: "/auth/refresh",
        method: "POST",
      }),
    }),
    googleHandshake: builder.mutation<TokenResponse, GoogleHandshakeRequest>({
      query: (body) => ({
        url: "/auth/google/handshake",
        method: "POST",
        body,
      }),
    }),
  }),
  overrideExisting: false,
})

export const {
  useRegisterMutation,
  useLoginMutation,
  useRefreshMutation,
  useGoogleHandshakeMutation,
} = authApi