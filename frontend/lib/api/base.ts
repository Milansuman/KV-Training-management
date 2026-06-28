import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const baseSlice = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.BACKEND_URL!
  }),
  endpoints: (builder) => ({})
})
