import { useState } from "react";
import { Link } from "react-router-dom";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { pct, useFetch } from "../api.js";
import Async from "../components/Async.jsx";
import SentimentBar from "../components/SentimentBar.jsx";
import Stamp from "../components/Stamp.jsx";

function Words({ sentiment }) {
  const state = useFetch(`/api/words?sentiment=${sentiment}&n=24`);
  return (
    <Async state={state}>
      {(words) => {
        const max = Math.max(...words.map((w) => w.count));
        return (
          <p className={`words words-${sentiment}`}>
            {words.map((w) => (
              <span key={w.word} style={{ fontSize: `${0.9 + 1.5 * (w.count / max)}rem` }} title={`${w.count} mentions`}>
                {w.word}
              </span>
            ))}
          </p>
        );
      }}
    </Async>
  );
}

function Heatmap() {
  const state = useFetch("/api/heatmap");
  return (
    <Async state={state}>
      {(h) => (
        <div className="table-wrap">
          <table className="heat">
            <thead>
              <tr>
                <th scope="col">Teacher</th>
                {h.topics.map((t) => <th key={t} scope="col">{t}</th>)}
              </tr>
            </thead>
            <tbody>
              {h.teachers.map((t, i) => (
                <tr key={t}>
                  <th scope="row">{t}</th>
                  {h.values[i].map((v, j) => (
                    <td key={j} style={v == null ? undefined : { background: `rgba(179, 32, 42, ${(v / 100) * 0.85})`, color: v > 55 ? "#fff" : "inherit" }}>
                      {v == null ? "–" : `${Math.round(v)}%`}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Async>
  );
}

export default function Overview() {
  const meta = useFetch("/api/meta");
  const [subject, setSubject] = useState("");
  const q = subject ? `?subject=${encodeURIComponent(subject)}` : "";

  const summary = useFetch(`/api/summary${q}`);
  const teachers = useFetch(`/api/teachers${q}`);
  const topics = useFetch(`/api/topics${q}`);
  const trend = useFetch(`/api/trend${q}`);
  const highlights = useFetch(`/api/highlights${q}`);

  return (
    <>
      <section className="hero">
        <Async state={summary}>
          {(s) => (
            <h1>
              {s.responses} students have rated their teachers. {pct(s.positive)} of what they wrote is positive,
              and the average rating is {s.avg_rating} out of 5.
            </h1>
          )}
        </Async>
        <div className="filter">
          <label htmlFor="subject">Subject</label>
          <select id="subject" value={subject} onChange={(e) => setSubject(e.target.value)}>
            <option value="">All subjects</option>
            {meta.data?.subjects.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </section>

      <section aria-labelledby="cards-h">
        <h2 id="cards-h">Report cards</h2>
        <p className="lede">Grade is based on the share of positive comments: A is 70% or more, B 55%, C 40%, D below that.</p>
        <Async state={teachers}>
          {(rows) => (
            <ul className="cards">
              {rows.map((t) => (
                <li key={t.teacher}>
                  <Link to={`/teachers/${encodeURIComponent(t.teacher)}`} className="card-row">
                    <span className="card-name">
                      <strong>{t.teacher}</strong>
                      <span className="muted">{t.subject}</span>
                    </span>
                    <span className="card-bar">
                      <SentimentBar positive={t.positive} neutral={t.neutral} negative={t.negative} />
                      <span className="muted small">
                        {pct(t.positive)} positive, {pct(t.negative)} negative, {t.responses} responses
                      </span>
                    </span>
                    <span className="card-rating"><strong>{t.avg_rating}</strong><span className="muted small"> / 5</span></span>
                    <Stamp grade={t.grade} animate />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </Async>
        <p className="legend">
          <span><i className="dot dot-positive" />Positive</span>
          <span><i className="dot dot-neutral" />Neutral</span>
          <span><i className="dot dot-negative" />Negative</span>
        </p>
      </section>

      <div className="two-col">
        <section aria-labelledby="topics-h">
          <h2 id="topics-h">Where students are unhappy</h2>
          <p className="lede">Share of negative comments by topic.</p>
          <Async state={topics}>
            {(rows) => (
              <ul className="hbars">
                {[...rows].sort((a, b) => b.negative - a.negative).map((r) => (
                  <li key={r.topic}>
                    <span className="hbar-label">{r.topic} <span className="muted small">({r.responses})</span></span>
                    <span className="hbar-track"><span className="hbar-fill" style={{ width: `${r.negative}%` }} /></span>
                    <span className="hbar-val">{pct(r.negative)}</span>
                  </li>
                ))}
              </ul>
            )}
          </Async>
        </section>

        <section aria-labelledby="trend-h">
          <h2 id="trend-h">Average rating by month</h2>
          <p className="lede">Each point is one month of feedback.</p>
          <Async state={trend}>
            {(rows) => (
              <div className="chart" role="img" aria-label="Line chart of average rating per month">
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={rows} margin={{ top: 8, right: 12, bottom: 0, left: -18 }}>
                    <CartesianGrid stroke="#D5DAE6" vertical={false} />
                    <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 5]} ticks={[0, 1, 2, 3, 4, 5]} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Line type="monotone" dataKey="avg_rating" name="Avg rating" stroke="#16213E" strokeWidth={2.5} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </Async>
        </section>
      </div>

      <div className="two-col">
        <Async state={highlights}>
          {(h) => (
            <>
              <section aria-labelledby="comp-h">
                <h2 id="comp-h">Most repeated complaints</h2>
                {h.complaints.length === 0 ? <p className="note">No negative comments yet.</p> : (
                  <ol className="quotes quotes-neg">
                    {h.complaints.map((c) => <li key={c.complaint}>{c.complaint}<span className="count">{c.count}×</span></li>)}
                  </ol>
                )}
              </section>
              <section aria-labelledby="praise-h">
                <h2 id="praise-h">Most repeated praise</h2>
                {h.praises.length === 0 ? <p className="note">No positive comments yet.</p> : (
                  <ol className="quotes quotes-pos">
                    {h.praises.map((c) => <li key={c.praise}>{c.praise}<span className="count">{c.count}×</span></li>)}
                  </ol>
                )}
              </section>
            </>
          )}
        </Async>
      </div>

      <section aria-labelledby="heat-h">
        <h2 id="heat-h">Teacher by topic</h2>
        <p className="lede">Darker red means a larger share of negative comments. This table covers all subjects.</p>
        <Heatmap />
      </section>

      <div className="two-col">
        <section aria-labelledby="wp-h">
          <h2 id="wp-h">Words in positive comments</h2>
          <Words sentiment="positive" />
        </section>
        <section aria-labelledby="wn-h">
          <h2 id="wn-h">Words in negative comments</h2>
          <Words sentiment="negative" />
        </section>
      </div>
    </>
  );
}
