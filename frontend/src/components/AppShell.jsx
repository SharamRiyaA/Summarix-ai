import { NavLink, useNavigate } from "react-router-dom";
import { getCurrentUser, logout } from "../api/auth";
import { useToast } from "./ToastProvider";

export default function AppShell({ title, description, children }) {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const user = getCurrentUser();
  const initials = (user?.username || "SU").slice(0, 2).toUpperCase();

  function handleLogout() {
    logout();
    addToast("You have been logged out.", "info");
    navigate("/login");
  }

  return (
    <main className="dashboard-shell">
      <section className="app-shell-modern">
        <header className="topbar card">
          <div className="topbar-brand">
            <span className="eyebrow">Summarix</span>
            <div>
              <h2>Modern Summary Hub</h2>
              <p>Fast summaries, saved history, and polished multimodal workflows in one place.</p>
            </div>
          </div>
          <nav className="topbar-nav">
            <NavLink
              to="/summarize"
              className={({ isActive }) => `nav-pill${isActive ? " nav-pill-active" : ""}`}
            >
              Summary
            </NavLink>
            <NavLink
              to="/history"
              className={({ isActive }) => `nav-pill${isActive ? " nav-pill-active" : ""}`}
            >
              History
            </NavLink>
          </nav>
          <div className="topbar-actions">
            <div className="profile-chip">
              <div className="profile-avatar">{initials}</div>
              <div className="profile-meta">
                <strong>{user?.username || "User"}</strong>
                <small>Profile</small>
              </div>
            </div>
            <button className="ghost-button" onClick={handleLogout} type="button">
              Logout
            </button>
          </div>
        </header>

        <section className="content-area content-area-wide">
          <header className="page-header card">
            <div>
              <span className="pill">{title}</span>
              <h1>{title}</h1>
              <p>{description}</p>
            </div>
          </header>
          {children}
        </section>
      </section>
    </main>
  );
}
