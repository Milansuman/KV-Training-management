import { baseSlice } from "../base"
import type {
  AnalyzeTrainingMaterialRequest,
  AnalyzeTrainingMaterialResponse,
} from "./training-materials.type"

export const aiTrainingMaterialsApi = baseSlice.injectEndpoints({
  endpoints: (builder) => ({
    analyzeTrainingMaterial: builder.mutation<
      AnalyzeTrainingMaterialResponse,
      AnalyzeTrainingMaterialRequest
    >({
      query: (body) => ({
        url: "/ai/training-materials/analyze",
        method: "POST",
        body,
      }),
    }),
  }),
})

export const { useAnalyzeTrainingMaterialMutation } = aiTrainingMaterialsApi
