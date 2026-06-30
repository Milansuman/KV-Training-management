export interface CreateProgramRequest {
  title: string;
  description: string;
  start_date: string; // YYYY-MM-DD
  end_date: string;   // YYYY-MM-DD
}

export interface UpdateProgramRequest {
  title?: string;
  description?: string;
  start_date?: string; // YYYY-MM-DD
  end_date?: string;   // YYYY-MM-DD
}

export interface ProgramResponse {
  id: number;
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  created_at: string;
}

export interface ProgramProgressItem {
  id: number;
  title: string;
  description: string;
  total_sessions: number;
  completed_sessions: number;
  created_at: string;
  updated_at: string;
  start_date: string;
  end_date: string;
}
