import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const baseSlice = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.NEXT_PUBLIC_BACKEND_URL!,
    credentials: 'include'
  }),
  endpoints: () => ({})
})
