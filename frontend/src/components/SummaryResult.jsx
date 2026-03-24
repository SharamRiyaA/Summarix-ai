import { useToast } from "./ToastProvider";

export default function SummaryResult({ item }) {
  const { addToast } = useToast();

  async function handleCopy() {
    if (!item?.summary) {
      return;
    }

    await navigator.clipboard.writeText(item.summary);
    addToast("Summary copied to clipboard.");
  }

  return (
    <section className="card stack">
      <div className="panel-header">
        <div>
          <span className="pill pill-soft">Latest summary</span>
          <h2>{item ? item.title : "No summary generated yet"}</h2>
          <p>
            {item
              ? `Saved on ${new Date(item.created_at).toLocaleString()}`
              : "Generate a summary from the form and the latest result will appear here."}
          </p>
        </div>
      </div>

      {item ? (
        <>
          <div className="result-toolbar">
            <div className="history-meta">
              <span className="history-badge">{item.input_type}</span>
              <span className="history-badge history-badge-muted">{item.output_format}</span>
              <span className="history-badge history-badge-muted">{item.summary_section?.replace("_", " ")}</span>
            </div>
            <button className="ghost-button" onClick={handleCopy} type="button">
              Copy
            </button>
          </div>
          <div className="result-block">
            <h3>Summary</h3>
            <p className="summary-text">{item.summary}</p>
          </div>
          {item.audio_url ? <audio controls src={item.audio_url} className="audio-player" /> : null}
        </>
      ) : (
        <div className="empty-state">
          <h3>Start with a new summary</h3>
          <p className="muted-text">Use the form to create a summary and it will be stored in SQLite automatically.</p>
        </div>
      )}
    </section>
  );
}
