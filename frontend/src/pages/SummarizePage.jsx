import { useEffect, useState } from "react";
import { api } from "../api/client";
import AppShell from "../components/AppShell";
import SummaryForm from "../components/SummaryForm";
import SummaryResult from "../components/SummaryResult";

export default function SummarizePage() {
  const [latestSummary, setLatestSummary] = useState(null);

  useEffect(() => {
    loadLatestSummary();
  }, []);

  async function loadLatestSummary() {
    const response = await api.get("/summaries/");
    setLatestSummary(response.data[0] ?? null);
  }

  function handleCreated(record) {
    setLatestSummary(record);
  }

  return (
    <AppShell
      title="Summarize"
      description="Create a fresh summary and immediately view the latest output on this page."
    >
      <section className="dashboard-grid">
        <SummaryForm onCreated={handleCreated} />
        <SummaryResult item={latestSummary} />
      </section>
    </AppShell>
  );
}
