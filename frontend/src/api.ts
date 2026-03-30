import type { ApiError, AskResponse, ProcessResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

function createApiError(status: number, detail: string): ApiError {
  const error = new Error(detail) as ApiError;
  error.status = status;
  error.detail = detail;
  return error;
}

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(async () => ({ detail: await response.text() }));
  if (!response.ok) {
    console.error("API error detail:", payload);
    throw createApiError(response.status, payload.detail ?? "Request failed.");
  }
  return payload as T;
}

export async function processVideo(input: {
  youtubeUrl: string;
  file: File | null;
  whisperModel: string;
  forceReprocess: boolean;
}): Promise<ProcessResponse> {
  const formData = new FormData();
  formData.append("youtube_url", input.youtubeUrl.trim());
  if (input.file) {
    formData.append("file", input.file);
  }
  formData.append("whisper_model", input.whisperModel);
  formData.append("force_reprocess", String(input.forceReprocess));

  const response = await fetch(`${API_BASE}/api/process`, {
    method: "POST",
    body: formData,
  });
  return parseResponse<ProcessResponse>(response);
}

export async function askQuestion(input: { videoId: string; question: string }): Promise<AskResponse> {
  const response = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_id: input.videoId, question: input.question }),
  });
  return parseResponse<AskResponse>(response);
}
