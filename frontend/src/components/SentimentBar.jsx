/** Stacked bar showing positive / neutral / negative share. */
export default function SentimentBar({ positive, neutral, negative, tall = false }) {
  const parts = [
    ["positive", positive],
    ["neutral", neutral],
    ["negative", negative],
  ];
  return (
    <div
      className={`sbar${tall ? " sbar-tall" : ""}`}
      role="img"
      aria-label={`${Math.round(positive)}% positive, ${Math.round(neutral)}% neutral, ${Math.round(negative)}% negative`}
    >
      {parts.map(([k, v]) => (
        <span key={k} className={`sbar-${k}`} style={{ width: `${v}%` }} />
      ))}
    </div>
  );
}
