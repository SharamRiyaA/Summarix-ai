import { useMemo, useState } from "react";
import { useToast } from "./ToastProvider";

export default function SummaryHistory({ items, onDelete }) {
  const { addToast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [sourceFilter, setSourceFilter] = useState("all");
  const [sectionFilter, setSectionFilter] = useState("all");
  const [sortOrder, setSortOrder] = useState("newest");

  const filteredItems = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    const nextItems = items.filter((item) => {
      const matchesSearch =
        !normalizedSearch ||
        item.title?.toLowerCase().includes(normalizedSearch) ||
        item.summary?.toLowerCase().includes(normalizedSearch);
      const matchesSource = sourceFilter === "all" || item.input_type === sourceFilter;
      const matchesSection = sectionFilter === "all" || item.summary_section === sectionFilter;
      return matchesSearch && matchesSource && matchesSection;
    });

    nextItems.sort((a, b) => {
      const aTime = new Date(a.created_at).getTime();
      const bTime = new Date(b.created_at).getTime();
      return sortOrder === "oldest" ? aTime - bTime : bTime - aTime;
    });

    return nextItems;
  }, [items, searchTerm, sourceFilter, sectionFilter, sortOrder]);

  async function handleCopy(summary) {
    await navigator.clipboard.writeText(summary);
    addToast("Summary copied to clipboard.");
  }

  function resetFilters() {
    setSearchTerm("");
    setSourceFilter("all");
    setSectionFilter("all");
    setSortOrder("newest");
  }

  return (
    <div className="history-shell">
      <div className="card history-filter-card stack">
        <div className="panel-header">
          <div>
            <span className="pill pill-soft">Library</span>
            <h2>Your saved summaries</h2>
            <p>Search, filter, and revisit past outputs with a cleaner history view.</p>
          </div>
          <div className="history-filter-stats">
            <div className="history-stat">
              <strong>{items.length}</strong>
              <span>Total</span>
            </div>
            <div className="history-stat">
              <strong>{filteredItems.length}</strong>
              <span>Visible</span>
            </div>
          </div>
        </div>
        <div className="history-filters">
          <label className="field-group history-filter-field">
            <span>Search</span>
            <input
              placeholder="Search by title or summary"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />
          </label>
          <label className="field-group history-filter-field">
            <span>Source</span>
            <select value={sourceFilter} onChange={(event) => setSourceFilter(event.target.value)}>
              <option value="all">All sources</option>
              <option value="text">Text</option>
              <option value="pdf">PDF</option>
              <option value="image">Image</option>
              <option value="youtube">YouTube</option>
            </select>
          </label>
          <label className="field-group history-filter-field">
            <span>Summary type</span>
            <select value={sectionFilter} onChange={(event) => setSectionFilter(event.target.value)}>
              <option value="all">All types</option>
              <option value="short_summary">Short Summary</option>
              <option value="key_points">Key Points</option>
            </select>
          </label>
          <label className="field-group history-filter-field">
            <span>Sort</span>
            <select value={sortOrder} onChange={(event) => setSortOrder(event.target.value)}>
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
            </select>
          </label>
          <button className="ghost-button history-reset-button" onClick={resetFilters} type="button">
            Clear filters
          </button>
        </div>
      </div>

      <div className="card stack">
      <div className="panel-header">
        <div>
          <span className="pill pill-soft">Results</span>
          <h2>History feed</h2>
          <p>Browse your saved summaries, copy what you need, and keep the list organized.</p>
        </div>
        <div className="status-chip">{filteredItems.length} showing</div>
      </div>
      <div className="history-list">
        {filteredItems.map((item) => (
          <article key={item.id} className="history-item">
            <div className="history-topline">
              <div className="history-meta">
                <span className="history-badge">{item.input_type}</span>
                <span className="history-badge history-badge-muted">{item.output_format}</span>
                <span className="history-badge history-badge-muted">{item.summary_section?.replace("_", " ")}</span>
              </div>
              <div className="history-actions">
                <button className="ghost-button" onClick={() => handleCopy(item.summary)} type="button">
                  Copy
                </button>
                <button className="ghost-button ghost-button-danger" onClick={() => onDelete(item.id)} type="button">
                  Delete
                </button>
              </div>
            </div>
            <div className="split-row split-row-start">
              <div className="history-copy">
                <h3>{item.title}</h3>
                <small>{new Date(item.created_at).toLocaleString()}</small>
              </div>
            </div>
            <p className="summary-text">{item.summary}</p>
            {item.audio_url ? <audio controls src={item.audio_url} className="audio-player" /> : null}
          </article>
        ))}
        {!filteredItems.length ? (
          <div className="empty-state">
            <h3>No matching summaries</h3>
            <p className="muted-text">Try changing the filters or create a new summary to populate your history.</p>
          </div>
        ) : null}
      </div>
    </div>
    </div>
  );
}
