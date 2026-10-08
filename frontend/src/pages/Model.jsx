import { useFetch } from "../api.js";
import Async from "../components/Async.jsx";

const f = (n) => (n == null ? "–" : n.toFixed(3));

export default function Model() {
  const state = useFetch("/api/model");
  return (
    <section>
      <h1>How well does the model work?</h1>
      <p className="lede">
        Tested on 90 comments the model never saw while training. VADER is a ready-made English tool used as a baseline.
      </p>
      <Async state={state}>
        {(m) => (
          <>
            <h2>Model comparison</h2>
            <div className="table-wrap">
              <table className="plain">
                <thead>
                  <tr><th scope="col">Model</th><th scope="col">Accuracy</th><th scope="col">Macro F1</th><th scope="col">Cross-validation</th></tr>
                </thead>
                <tbody>
                  {m.results.map((r) => (
                    <tr key={r.model} className={r.model === m.best_model ? "best" : ""}>
                      <th scope="row">{r.model}{r.model === m.best_model && " (used)"}</th>
                      <td>{f(r.accuracy)}</td><td>{f(r.f1_macro)}</td><td>{f(r.cv_accuracy)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="note">
              VADER only understands English, so it misreads Hinglish like "samajh nahi aata". That is why we trained our own model.
            </p>

            <h2>Performance by class</h2>
            <div className="table-wrap">
              <table className="plain">
                <thead>
                  <tr><th scope="col">Class</th><th scope="col">Precision</th><th scope="col">Recall</th><th scope="col">F1</th><th scope="col">Test comments</th></tr>
                </thead>
                <tbody>
                  {m.report.map((r) => (
                    <tr key={r.label}>
                      <th scope="row" className={`tone-${r.label}`}>{r.label}</th>
                      <td>{r.precision.toFixed(2)}</td><td>{r.recall.toFixed(2)}</td><td>{r.f1.toFixed(2)}</td><td>{r.support}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="note">Neutral is the weakest class because there are far fewer neutral comments to learn from.</p>

            <div className="two-col imgs">
              <figure>
                <img src="/api/outputs/confusion_matrix.png" alt="Confusion matrix of predicted against actual sentiment" />
                <figcaption>Confusion matrix: rows are the true label, columns are what the model predicted.</figcaption>
              </figure>
              <figure>
                <img src="/api/outputs/model_comparison.png" alt="Bar chart comparing model accuracy" />
                <figcaption>Test accuracy of each model.</figcaption>
              </figure>
            </div>
          </>
        )}
      </Async>
    </section>
  );
}
