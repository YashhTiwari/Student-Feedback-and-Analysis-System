/** Shows loading / error states, otherwise renders children(data). */
export default function Async({ state, children }) {
  if (state.loading && !state.data) return <p className="note" aria-live="polite">Loading…</p>;
  if (state.error) return <p className="error" role="alert">{state.error}</p>;
  if (!state.data) return null;
  return children(state.data);
}
