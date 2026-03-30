export function ModelSelector(props: { value: string; onChange: (value: string) => void }) {
  return (
    <div className="panel block-stack">
      <label className="field">
        <span>Whisper model</span>
        <select value={props.value} onChange={(event) => props.onChange(event.target.value)}>
          <option value="tiny">tiny - fastest, basic accuracy</option>
          <option value="base">base - recommended</option>
          <option value="small">small - better accuracy</option>
          <option value="medium">medium - best accuracy, slower</option>
        </select>
      </label>
      <p className="hint">base recommended for most videos</p>
    </div>
  );
}
