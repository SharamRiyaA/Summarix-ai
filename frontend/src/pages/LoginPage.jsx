import AuthForm from "../components/AuthForm";

export default function LoginPage() {
  return (
    <main className="auth-shell">
      <section className="auth-showcase">
        <div className="auth-copy">
          <span className="eyebrow">AI Content Studio</span>
          <h1>Turn long content into sharp, usable notes in seconds.</h1>
          <p>
            Summarix gives you a clean space for text, PDFs, images, and YouTube links, then turns them into focused
            summaries you can save, copy, and revisit anytime.
          </p>
          <div className="login-showcase">
            <article className="login-hero-card">
              <div className="login-hero-copy">
                <span className="pill pill-soft">Built for fast reading</span>
                <h2>Readable results, better flow</h2>
                <p>
                  Generate concise summaries, pull key points, and keep everything organized in one modern dashboard.
                </p>
              </div>
              <div className="login-metric-grid">
                <div className="login-metric">
                  <strong>4</strong>
                  <span>input types</span>
                </div>
                <div className="login-metric">
                  <strong>2</strong>
                  <span>result modes</span>
                </div>
                <div className="login-metric">
                  <strong>1</strong>
                  <span>clean workspace</span>
                </div>
              </div>
            </article>
            <div className="feature-grid feature-grid-login">
              <article className="feature-tile">
                <strong>Multimodal</strong>
                <span>Text, PDF, image OCR, and YouTube transcript summaries in one place.</span>
              </article>
              <article className="feature-tile">
                <strong>Copy-ready</strong>
                <span>Use short summaries or key points instantly without reformatting them yourself.</span>
              </article>
              <article className="feature-tile">
                <strong>Saved history</strong>
                <span>Keep previous results organized so you can return to them whenever you need.</span>
              </article>
            </div>
          </div>
        </div>
        <AuthForm />
      </section>
    </main>
  );
}
