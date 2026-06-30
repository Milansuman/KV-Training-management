import { createApi } from '@reduxjs/toolkit/query/react'
import type { BaseQueryFn } from '@reduxjs/toolkit/query'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL!

const autoRefreshBaseQuery = (): BaseQueryFn<
  {
    url: string
    method?: string
    body?: object | FormData
    formData?: boolean
  },
  unknown,
  unknown
> => {
  return async ({ url, method, body, formData }) => {
    const makeRequest = (): Promise<Response> =>
      fetch(`${BACKEND_URL}${url}`, {
        method: method ?? 'GET',
        credentials: 'include',
        headers: formData
          ? {}
          : { 'Content-Type': 'application/json' },
        body: body
          ? formData
            ? (body as FormData)
            : JSON.stringify(body)
          : undefined,
      })

    let response = await makeRequest()

    // If the server rejected the access token, try to refresh the token pair
    // via the httpOnly refresh cookie and then retry the original request.
    if (response.status === 401) {
      const refreshResponse = await fetch(`${BACKEND_URL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      })

      if (refreshResponse.ok) {
        // New cookies were set — retry the original request with the fresh
        // access token that is now attached to the cookie jar.
        response = await makeRequest()
      } else {
        // Refresh failed (e.g. the refresh token itself is expired).
        // Return the original 401 error so the calling code can route the
        // user to the login page.
        const errorBody = await response.json().catch(() => null)
        return { error: errorBody ?? { detail: 'Unauthorized' } }
      }
    }

    const responseBody = await response.json().catch(() => null)

    if (!response.ok) {
      return { error: responseBody ?? { detail: response.statusText } }
    }

    return { data: responseBody }
  }
}

export const baseSlice = createApi({
  reducerPath: 'api',
  baseQuery: autoRefreshBaseQuery(),
  tagTypes: ['Program', 'Session', 'Topic', 'User', 'TrainingMaterial', 'ProgramPermission', 'SessionPermission', 'Feedback', 'FeedbackSubmission', 'Assignment', 'AssignmentSubmission'],
  endpoints: () => ({}),
})
