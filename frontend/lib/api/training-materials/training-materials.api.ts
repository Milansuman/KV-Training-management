import { baseSlice } from "../base"
import { TrainingMaterialResponse } from "./training-materials.type"

export const trainingMaterialsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    uploadTrainingMaterial: builder.mutation<
      TrainingMaterialResponse,
      { title: string; session_id: number; user_id: number; file: File }
    >({
      query: ({ title, session_id, user_id, file }) => {
        const formData = new FormData()
        formData.append("title", title)
        formData.append("session_id", String(session_id))
        formData.append("user_id", String(user_id))
        formData.append("file", file)
        return {
          url: "/training-materials",
          method: "POST",
          body: formData,
          formData: true,
        }
      },
      invalidatesTags: ["TrainingMaterial"],
    }),

    createMaterialFromUrl: builder.mutation<
      TrainingMaterialResponse,
      { title: string; url: string; session_id: number; user_id: number }
    >({
      query: ({ title, url, session_id, user_id }) => {
        const formData = new FormData()
        formData.append("title", title)
        formData.append("url", url)
        formData.append("session_id", String(session_id))
        formData.append("user_id", String(user_id))
        return {
          url: "/training-materials/url",
          method: "POST",
          body: formData,
          formData: true,
        }
      },
      invalidatesTags: ["TrainingMaterial"],
    }),

    getTrainingMaterials: builder.query<TrainingMaterialResponse[], void>({
      query: () => ({
        url: "/training-materials",
        method: "GET",
      }),
      providesTags: ["TrainingMaterial"],
    }),

    getTrainingMaterialsBySession: builder.query<
      TrainingMaterialResponse[],
      number
    >({
      query: (sessionId) => ({
        url: `/training-materials/${sessionId}`,
        method: "GET",
      }),
      providesTags: ["TrainingMaterial"],
    }),

    updateTrainingMaterial: builder.mutation<
      TrainingMaterialResponse,
      {
        materialId: number
        title: string
        file?: File | null
        url?: string | null
      }
    >({
      query: ({ materialId, title, file, url }) => {
        const formData = new FormData()
        formData.append("title", title)

        if (file) formData.append("file", file)
        if (url) formData.append("url", url)
        return {
          url: `/training-materials/${materialId}`,
          method: "PUT",
          body: formData,
          formData: true,
        }
      },
      invalidatesTags: ["TrainingMaterial"],
    }),

    deleteTrainingMaterial: builder.mutation<
      { detail: string },
      number
    >({
      query: (materialId) => ({
        url: `/training-materials/${materialId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["TrainingMaterial"],
    }),
  }),
})

export const {
  useUploadTrainingMaterialMutation,
  useCreateMaterialFromUrlMutation,
  useGetTrainingMaterialsQuery,
  useGetTrainingMaterialsBySessionQuery,
  useUpdateTrainingMaterialMutation,
  useDeleteTrainingMaterialMutation,
} = trainingMaterialsApi
