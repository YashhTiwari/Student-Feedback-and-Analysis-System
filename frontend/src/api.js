import { useEffect, useState } from "react";

const BASE = import.meta.env.VITE_API_URL ?? "";

async function request(path, options) {
  let res;
  try {
    res = await fetch(BASE + path, options);
  } catch {
    throw new Error("Can't reach the server. Start the backend with: uvicorn api.main:app --port 8000");
  }
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") msg = body.detail;
      else if (Array.isArray(body.detail)) msg = body.detail.map((d) => `${d.loc?.slice(-1)[0]}: ${d.msg}`).join("; ");
    } catch { /* keep default message */ }
    throw new Error(msg);
  }
  return res.json();
}

export const api = {
  get: (path) => request(path),
  post: (path, body) =>
    request(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
};

/** Fetch JSON from the API and track loading / error state. Re-fetches when `path` changes. */
export function useFetch(path) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));
    api.get(path)
      .then((data) => !cancelled && setState({ data, error: null, loading: false }))
      .catch((error) => !cancelled && setState({ data: null, error: error.message, loading: false }));
    return () => { cancelled = true; };
  }, [path]);
  return state;
}

export const pct = (n) => `${Math.round(n)}%`;
