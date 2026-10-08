import { Link, useParams } from "react-router-dom";
import { pct, useFetch } from "../api.js";
import Async from "../components/Async.jsx";
import SentimentBar from "../components/SentimentBar.jsx";
import Stamp from "../components/Stamp.jsx";

export default function Teacher() {
  const { name } = useParams();
  const state = useFetch(`/api/teachers/${encodeURIComponent(name)}`);

  return (
    <Async state={state}>
      {(t) => (
        <>
          <p><Link to="/" className="back">Back to all teachers</Link></p>
          <header className="teacher-head">
            <div>
              <h1>{t.teacher}</h1>
              <p className="lede">{t.subject}</p>
            </div>
            <Stamp grade={t.grade} size="lg" />
          </header>

          <p className="summary">{t.summary}</p>

          <dl className="stats">
            <div><dt>Responses</dt><dd>{t.responses}</dd></div>
            <div><dt>Average rating</dt><dd>{t.avg_rating}<span className="muted small"> / 5</span></dd></div>
            <div><dt>Positive</dt><dd>{pct(t.positive)}</dd></div>
            <div><dt>Negative</dt><dd>{pct(t.negative)}</dd></div>
          </dl>

          <section aria-labelledby="tt-h">
            <h2 id="tt-h">How each topic is going</h2>
            <ul className="topic-rows">
              {t.topics.map((r) => (
                <li key={r.topic}>
                  <span className="topic-name">{r.topic} <span className="muted small">({r.responses})</span></span>
                  <SentimentBar positive={r.positive} neutral={r.neutral} negative={r.negative} />
                  <span className="topic-neg small">{pct(r.negative)} negative</span>
                </li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="neg-h">
            <h2 id="neg-h">Recent negative comments</h2>
            {t.recent_negative.length === 0 ? <p className="note">No negative comments yet.</p> : (
              <ul className="comments">
                {t.recent_negative.map((c, i) => (
                  <li key={i}>
                    <p>{c.comment}</p>
                    <span className="muted small">{c.date}, rated {c.rating}, {c.topic}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section aria-labelledby="mm-h">
            <h2 id="mm-h">Rating and comment disagree</h2>
            <p className="lede">The star rating points one way and the comment text points the other.</p>
            {t.mismatches.length === 0 ? <p className="note">None found.</p> : (
              <div className="table-wrap">
                <table className="plain">
                  <thead>
                    <tr><th scope="col">Rating</th><th scope="col">Rating suggests</th><th scope="col">Comment reads as</th><th scope="col">Comment</th></tr>
                  </thead>
                  <tbody>
                    {t.mismatches.map((m, i) => (
                      <tr key={i}>
                        <td>{m.rating}</td>
                        <td className={`tone-${m.rating_says}`}>{m.rating_says}</td>
                        <td className={`tone-${m.predicted_sentiment}`}>{m.predicted_sentiment}</td>
                        <td>{m.comment}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </Async>
  );
}
