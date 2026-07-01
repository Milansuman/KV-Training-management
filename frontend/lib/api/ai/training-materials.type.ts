export interface AnalyzeTrainingMaterialRequest {
  material_url: string
  topics: string[]
}

export interface AnalyzeTrainingMaterialResponse {
  material_url: string
  suggestions: string
}
