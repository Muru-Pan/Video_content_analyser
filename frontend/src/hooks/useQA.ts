import { useState } from "react";

import { askQuestion } from "../api";
import type { ApiError, AskResponse } from "../types";

export function useQA() {
  const [data, setData] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  async function submit(videoId: string, question: string) {
    setLoading(true);
    setError(null);
    try {
      const response = await askQuestion({ videoId, question });
      setData(response);
      return response;
    } catch (err) {
      setData(null);
      setError(err as ApiError);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return { data, loading, error, submit, setError };
}
