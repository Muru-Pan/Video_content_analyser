export function SummaryPanel(props: { title: string; category: string; summary: string }) {
  return (
    <div className="panel summary-panel">
      <div className="summary-title-row">
        <div>
          <p className="eyebrow">Generated title</p>
          <h2>{props.title || "Generated title will appear here."}</h2>
        </div>
        <span className="badge badge-strong">{props.category || "Uncategorized"}</span>
      </div>
      <p>{props.summary || "Summary will appear here after processing."}</p>
    </div>
  );
}
