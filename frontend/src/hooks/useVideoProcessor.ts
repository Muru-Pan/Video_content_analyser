import { useState } from "react";

import { processVideo } from "../api";
import type { ApiError, ProcessResponse } from "../types";

export function useVideoProcessor() {
  const [data, setData] = useState<ProcessResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [stepLabel, setStepLabel] = useState("");

  async function analyze(input: {
    youtubeUrl: string;
    file: File | null;
    whisperModel: string;
    forceReprocess: boolean;
  }) {
    setLoading(true);
    setError(null);
    setStepLabel("Starting analysis...");
    try {
      setStepLabel(input.youtubeUrl ? "Downloading audio..." : "Preparing upload...");
      const result = await processVideo(input);
      setStepLabel("Done");
      setData(result);
      return result;
    } catch (err) {
      setData(null);
      setError(err as ApiError);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return { data, loading, error, stepLabel, analyze, setError };
}
