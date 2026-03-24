import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { storeTokens } from "../api/auth";
import { useToast } from "./ToastProvider";

export default function AuthForm() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [isRegistering, setIsRegistering] = useState(false);
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    try {
      if (isRegistering) {
        await api.post("/auth/register/", form);
        addToast("Account created successfully. Signing you in now.");
      }
      const response = await api.post("/auth/login/", {
        username: form.username,
        password: form.password
      });
      storeTokens(response.data);
      addToast(`Welcome back, ${response.data.user?.username || form.username}.`);
      navigate("/");
    } catch (requestError) {
      setError("Authentication failed. Please check your details and try again.");
    }
  }

  return (
    <div className="card auth-card">
      <div className="auth-card-header">
        <span className="pill pill-soft">{isRegistering ? "Create account" : "Welcome back"}</span>
        <h2>{isRegistering ? "Start your modern summary space." : "Sign in and continue where you left off."}</h2>
        <p>Secure access, fast summaries, saved history, and a cleaner workflow every time you log in.</p>
      </div>
      <form onSubmit={handleSubmit} className="stack">
        <label className="field-group">
          <span>Username</span>
          <input
            placeholder="Enter your username"
            value={form.username}
            onChange={(event) => setForm({ ...form, username: event.target.value })}
            required
          />
        </label>
        {isRegistering ? (
          <label className="field-group">
            <span>Email</span>
            <input
              type="email"
              placeholder="Enter your email"
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
            />
          </label>
        ) : null}
        <label className="field-group">
          <span>Password</span>
          <input
            type="password"
            placeholder="Enter your password"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            required
          />
        </label>
        {error ? <div className="error-text">{error}</div> : null}
        <button className="auth-submit" type="submit">{isRegistering ? "Create account" : "Login"}</button>
      </form>
      <div className="auth-switcher">
        <span>{isRegistering ? "Already have an account?" : "Need an account?"}</span>
        <button className="ghost-button auth-switch-button" onClick={() => setIsRegistering(!isRegistering)} type="button">
          {isRegistering ? "Login instead" : "Register instead"}
        </button>
      </div>
    </div>
  );
}
