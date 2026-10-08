import { useState } from "react";
import { api, pct, useFetch } from "../api.js";
import Async from "../components/Async.jsx";

const RATING_LABELS = { 1: "Poor", 2: "Weak", 3: "Okay", 4: "Good", 5: "Excellent" };

export default function Feedback() {
  const meta = useFetch("/api/meta");
  const [teacher, setTeacher] = useState("");
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const teachers = meta.data?.teachers ?? [];
  const subject = teachers.find((t) => t.name === teacher)?.subject;
  const ready = teacher && rating && comment.trim().length >= 5;

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      setResult(await api.post("/api/feedback", { teacher, rating, comment }));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    setResult(null);
    setRating(0);
    setComment("");
    setError("");
  }

  if (result) {
    return (
      <section className="narrow" aria-live="polite">
        <h1>Thanks, your feedback is saved.</h1>
        <p className="lede">
          Our model read your comment as <strong className={`tone-${result.sentiment}`}>{result.sentiment}</strong>
          {" "}({pct(result.confidence * 100)} sure) and about <strong>{result.topic}</strong>.
          It now counts in the teacher's report card.
        </p>
        <button className="btn" onClick={reset}>Write more feedback</button>
      </section>
    );
  }

  return (
    <section className="narrow">
      <h1>Give feedback on a teacher</h1>
      <p className="lede">Write in English or Hinglish. Say what worked and what did not.</p>
      <Async state={meta}>
        {() => (
          <form onSubmit={submit} className="form">
            <div className="field">
              <label htmlFor="teacher">Teacher</label>
              <select id="teacher" value={teacher} onChange={(e) => setTeacher(e.target.value)} required>
                <option value="">Choose a teacher</option>
                {teachers.map((t) => <option key={t.name} value={t.name}>{t.name}</option>)}
              </select>
              {subject && <span className="hint">Subject: {subject}</span>}
            </div>

            <fieldset className="field">
              <legend>Rating</legend>
              <div className="rating">
                {[1, 2, 3, 4, 5].map((n) => (
                  <label key={n} className={rating === n ? "on" : ""}>
                    <input type="radio" name="rating" value={n} checked={rating === n} onChange={() => setRating(n)} />
                    <span className="rating-n">{n}</span>
                    <span className="rating-t">{RATING_LABELS[n]}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            <div className="field">
              <label htmlFor="comment">Your comment</label>
              <textarea
                id="comment"
                rows={5}
                maxLength={500}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Example: Sir samjhate achhe se hain, but lab mein computers kaam nahi karte."
              />
              <span className="hint">{comment.length} / 500 (at least 5 characters)</span>
            </div>

            {error && <p className="error" role="alert">{error}</p>}
            <button className="btn" type="submit" disabled={!ready || busy}>
              {busy ? "Saving…" : "Submit feedback"}
            </button>
          </form>
        )}
      </Async>
    </section>
  );
}
