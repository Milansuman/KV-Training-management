export interface TopicCreateRequest {
  title: string;
}

export interface TopicUpdateRequest {
  title: string;
}

export interface TopicResponse {
  id: number;
  title: string;
}
