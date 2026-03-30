import type { Source } from "../types";

export function SourceCard(props: { source: Source; onJump?: (seconds: number) => void }) {
  return (
    <article className="source-card">
      <div className="result-head">
        <span className="timestamp-chip">{props.source.timestamp}</span>
        <button className="ghost-button" type="button" onClick={() => props.onJump?.(props.source.start_seconds)}>
          Jump to {props.source.timestamp}
        </button>
      </div>
      <p>{props.source.text.length > 220 ? `${props.source.text.slice(0, 220)}...` : props.source.text}</p>
    </article>
  );
}
