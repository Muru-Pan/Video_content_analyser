import { FormEvent, useRef, useState } from "react";

import { ModelSelector } from "./components/ModelSelector";
import { ProgressBar } from "./components/ProgressBar";
import { QAPanel } from "./components/QAPanel";
import { SummaryPanel } from "./components/SummaryPanel";
import { TranscriptPanel } from "./components/TranscriptPanel";
import { VideoInput } from "./components/VideoInput";
import { YouTubePlayer, type YouTubePlayerHandle } from "./components/YouTubePlayer";
import { useQA } from "./hooks/useQA";
import { useVideoProcessor } from "./hooks/useVideoProcessor";

export default function App() {
  const [mode, setMode] = useState<"youtube" | "upload">("youtube");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [whisperModel, setWhisperModel] = useState("base");
  const [forceReprocess, setForceReprocess] = useState(false);
  const [question, setQuestion] = useState("");
  const playerRef = useRef<YouTubePlayerHandle>(null);
  const processor = useVideoProcessor();
  const qa = useQA();

  async function handleAnalyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    qa.setError(null);
    await processor.analyze({
      youtubeUrl: mode === "youtube" ? youtubeUrl : "",
      file: mode === "upload" ? file : null,
      whisperModel,
      forceReprocess,
    });
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!processor.data?.video_id) {
      return;
    }
    await qa.submit(processor.data.video_id, question);
  }

  function handleJump(seconds: number) {
    playerRef.current?.seekTo(seconds);
  }

  return (
    <div className="shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <main className="app-frame">
        <section className="hero">
          <p className="eyebrow">Production Release 1.0.0</p>
          <h1>Video Content Analyzer</h1>
          <p className="lede">
            Turn lectures, tutorials, and recorded sessions into searchable study assets with local AI, timestamp-linked answers, and direct video navigation.
          </p>
        </section>

        <div className="dashboard-grid">
          <form className="block-stack" onSubmit={handleAnalyze}>
            <VideoInput
              mode={mode}
              onModeChange={setMode}
              youtubeUrl={youtubeUrl}
              onYoutubeUrlChange={(value) => {
                setYoutubeUrl(value);
                if (value) {
                  setFile(null);
                }
              }}
              file={file}
              onFileChange={(next) => {
                setFile(next);
                if (next) {
                  setYoutubeUrl("");
                }
              }}
            />
            <ModelSelector value={whisperModel} onChange={setWhisperModel} />
            <label className="panel toggle-panel">
              <input type="checkbox" checked={forceReprocess} onChange={(event) => setForceReprocess(event.target.checked)} />
              <span>Rebuild transcript and index even if cached artifacts exist</span>
            </label>
            <button className="primary-button big" type="submit" disabled={processor.loading}>
              {processor.loading ? "Analyzing..." : "Analyze"}
            </button>
            {processor.error ? <p className="error-banner">{processor.error.detail}</p> : null}
          </form>

          <div className="block-stack">
            <ProgressBar loading={processor.loading} label={processor.stepLabel || processor.data?.status || "Waiting for input."} />
            <SummaryPanel
              title={processor.data?.title ?? ""}
              category={processor.data?.category ?? ""}
              summary={processor.data?.summary ?? ""}
            />
            {processor.data?.source_url ? <YouTubePlayer ref={playerRef} url={processor.data.source_url} /> : null}
          </div>
        </div>

        <div className="content-grid">
          <TranscriptPanel transcript={processor.data?.transcript ?? ""} segments={processor.data?.segments ?? []} onJump={processor.data?.source_url ? handleJump : undefined} />
          <QAPanel
            disabled={!processor.data?.video_id}
            question={question}
            onQuestionChange={setQuestion}
            onSubmit={handleAsk}
            loading={qa.loading}
            answer={qa.data?.answer ?? ""}
            sources={qa.data?.sources ?? []}
            error={qa.error?.detail ?? ""}
            onJump={processor.data?.source_url ? handleJump : undefined}
          />
        </div>
      </main>
    </div>
  );
}
