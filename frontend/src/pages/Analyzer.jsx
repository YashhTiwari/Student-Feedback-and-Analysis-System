import { useState } from "react";
import { api, pct } from "../api.js";

const EXAMPLES = [
  "Sir bahut accha padhate hain, samajh aa jata hai",
  "Lab mein computers kaam nahi karte, practical ho hi nahi paata",
  "Paper was okay, nothing special",
  "Teaching is good but the exam was unfair",
];

export default function Analyzer() {
  const [text, setText] = useState("");
  const [res, setRes] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run(value = text) {
    setBusy(true);
    setError("");
    try {
      setRes(await api.post("/api/predict", { comment: value }));
    } catch (err) {
      setError(err.message);
      setRes(null);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="narrow">
      <h1>Analyze a comment</h1>
      <p className="lede">Paste any student comment to see how the model reads it. Nothing is saved.</p>

      <div className="field">
        <label htmlFor="text">Comment</label>
        <textarea id="text" rows={4} maxLength={500} value={text} onChange={(e) => setText(e.target.value)} />
      </div>
      <div className="examples">
        <span className="muted small">Try an example:</span>
        {EXAMPLES.map((ex) => (
          <button key={ex} className="chip" onClick={() => { setText(ex); run(ex); }}>{ex}</button>
        ))}
      </div>
      <button className="btn" disabled={text.trim().length < 3 || busy} onClick={() => run()}>
        {busy ? "Analyzing…" : "Analyze comment"}
      </button>

      {error && <p className="error" role="alert">{error}</p>}

      <div aria-live="polite">
        {res && (
          <div className="result">
            <p className="result-head">
              The model reads this as <strong className={`tone-${res.sentiment} big`}>{res.sentiment}</strong>
              {" "}({pct(res.confidence * 100)} sure), about <strong>{res.topic}</strong>.
            </p>
            <ul className="hbars">
              {["positive", "neutral", "negative"].map((k) => (
                <li key={k}>
                  <span className="hbar-label">{k}</span>
                  <span className="hbar-track"><span className={`hbar-fill fill-${k}`} style={{ width: `${res.probabilities[k] * 100}%` }} /></span>
                  <span className="hbar-val">{pct(res.probabilities[k] * 100)}</span>
                </li>
              ))}
            </ul>
            <details>
              <summary>Text the model actually sees</summary>
              <p className="mono-text">{res.cleaned || "(empty after cleaning)"}</p>
            </details>
          </div>
        )}
      </div>
    </section>
  );
}
