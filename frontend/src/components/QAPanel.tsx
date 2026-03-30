import type { FormEvent } from "react";

import type { Source } from "../types";
import { SourceCard } from "./SourceCard";

export function QAPanel(props: {
  disabled: boolean;
  question: string;
  onQuestionChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  loading: boolean;
  answer: string;
  sources: Source[];
  error: string;
  onJump?: (seconds: number) => void;
}) {
  return (
    <div className="panel qa-panel">
      <form className="block-stack" onSubmit={props.onSubmit}>
        <div className="result-head">
          <h2>Ask the video</h2>
          <span className="badge">{props.disabled ? "Locked" : "Ready"}</span>
        </div>
        <textarea rows={4} value={props.question} onChange={(event) => props.onQuestionChange(event.target.value)} placeholder="What is the main idea of this lesson?" disabled={props.disabled} />
        <button className="primary-button" type="submit" disabled={props.disabled || props.loading}>
          {props.loading ? "Asking..." : "Ask"}
        </button>
        {props.error ? <p className="error-banner">{props.error}</p> : null}
      </form>

      <div className="answer-box">
        <h3>Answer</h3>
        <p>{props.answer || "Answers will appear here after you ask a question."}</p>
      </div>

      <div className="block-stack">
        <h3>Sources</h3>
        {props.sources.length > 0 ? props.sources.map((source) => (
          <SourceCard key={`${source.chunk_index}-${source.start_seconds}`} source={source} onJump={props.onJump} />
        )) : <p className="hint">Source passages will appear here with timestamp jump actions.</p>}
      </div>
    </div>
  );
}
