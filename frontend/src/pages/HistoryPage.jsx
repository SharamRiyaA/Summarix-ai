import { useEffect, useState } from "react";
import { api } from "../api/client";
import AppShell from "../components/AppShell";
import SummaryHistory from "../components/SummaryHistory";
import { useToast } from "../components/ToastProvider";

export default function HistoryPage() {
  const { addToast } = useToast();
  const [items, setItems] = useState([]);

  useEffect(() => {
    loadSummaries();
  }, []);

  async function loadSummaries() {
    const response = await api.get("/summaries/");
    setItems(response.data);
  }

  async function handleDelete(id) {
    await api.delete(`/summaries/${id}/delete/`);
    setItems((current) => current.filter((item) => item.id !== id));
    addToast("Summary removed from history.");
  }

  return (
    <AppShell
      title="Previous History"
      description="Browse the summaries already saved for your account and remove anything you no longer need."
    >
      <SummaryHistory items={items} onDelete={handleDelete} />
    </AppShell>
  );
}
