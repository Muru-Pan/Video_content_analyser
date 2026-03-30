export interface Segment {
  start: number;
  end: number;
  text: string;
}

export interface ProcessResponse {
  video_id: string;
  audio_path: string;
  transcript: string;
  segments: Segment[];
  summary: string;
  title: string;
  category: string;
  status: string;
  source_url?: string;
}

export interface Source {
  text: string;
  timestamp: string;
  start_seconds: number;
  chunk_index: number;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export interface ApiError extends Error {
  status: number;
  detail: string;
}
