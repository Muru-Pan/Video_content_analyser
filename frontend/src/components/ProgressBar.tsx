export function ProgressBar(props: { loading: boolean; label: string }) {
  return (
    <div className="panel block-stack">
      <div className="result-head">
        <h2>Progress</h2>
        <span className="badge">{props.loading ? "Working" : "Idle"}</span>
      </div>
      <div className="progress-rail">
        <div className={props.loading ? "progress-fill loading" : "progress-fill done"} />
      </div>
      <p>{props.label || "Waiting for a new job."}</p>
    </div>
  );
}
