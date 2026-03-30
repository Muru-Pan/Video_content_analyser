import type { ChangeEvent } from "react";

export function VideoInput(props: {
  mode: "youtube" | "upload";
  onModeChange: (mode: "youtube" | "upload") => void;
  youtubeUrl: string;
  onYoutubeUrlChange: (value: string) => void;
  file: File | null;
  onFileChange: (file: File | null) => void;
}) {
  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    props.onFileChange(event.target.files?.[0] ?? null);
  }

  return (
    <div className="panel block-stack">
      <div className="pill-switch">
        <button className={props.mode === "youtube" ? "switch active" : "switch"} onClick={() => props.onModeChange("youtube")} type="button">YouTube URL</button>
        <button className={props.mode === "upload" ? "switch active" : "switch"} onClick={() => props.onModeChange("upload")} type="button">Upload File</button>
      </div>

      {props.mode === "youtube" ? (
        <label key="youtube-mode" className="field">
          <span>YouTube URL</span>
          <input type="url" value={props.youtubeUrl ?? ""} onChange={(event) => props.onYoutubeUrlChange(event.target.value)} placeholder="https://www.youtube.com/watch?v=..." />
        </label>
      ) : (
        <label key="upload-mode" className="field upload-zone">
          <span>Media file</span>
          <input type="file" accept=".mp4,.mp3,.wav,.m4a,.webm,video/*,audio/*" onChange={handleFileChange} />
          <small>{props.file ? `${props.file.name} (${Math.round(props.file.size / 1024)} KB)` : "Accepted: .mp4, .mp3, .wav, .m4a, .webm"}</small>
        </label>
      )}
    </div>
  );
}
