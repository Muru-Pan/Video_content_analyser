import type { Segment } from "../types";

export function TranscriptPanel(props: { transcript: string; segments: Segment[]; onJump?: (seconds: number) => void }) {
  return (
    <div className="panel block-stack transcript-panel">
      <div className="result-head">
        <h2>Transcript</h2>
        <button type="button" className="ghost-button" onClick={() => navigator.clipboard.writeText(props.transcript)}>Copy transcript</button>
      </div>
      <div className="segment-list">
        {props.segments.length > 0 ? props.segments.map((segment, index) => {
          const timestamp = new Date(segment.start * 1000).toISOString().substring(segment.start >= 3600 ? 11 : 14, 19);
          return (
            <button key={`${segment.start}-${index}`} className="segment-row" type="button" onClick={() => props.onJump?.(segment.start)}>
              <span className="timestamp-chip">{timestamp}</span>
              <span>{segment.text}</span>
            </button>
          );
        }) : <pre>{props.transcript || "Transcript output will appear here."}</pre>}
      </div>
    </div>
  );
}
