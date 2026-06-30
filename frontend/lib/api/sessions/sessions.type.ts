export interface SessionCreateRequest {
  title: string;
  description: string;
  start_datetime: string; // ISO datetime string
  end_datetime: string;   // ISO datetime string
  program_id: number;
}

export interface SessionUpdateRequest {
  title: string;
  description: string;
  start_datetime: string; // ISO datetime string
  end_datetime: string;   // ISO datetime string
}

export interface SessionResponse {
  id: number;
  title: string;
  description: string;
  start_datetime: string;
  end_datetime: string;
  program_id: number;
  feedback_id: number | null;
}

export interface TopicResponse {
  id: number;
  title: string;
}

export interface SessionResponseWithTopics extends SessionResponse {
  topics: TopicResponse[];
}
