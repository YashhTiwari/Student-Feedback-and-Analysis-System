const GRADE_NOTE = { A: "Excellent", B: "Good", C: "Needs attention", D: "Needs urgent improvement" };

/** Red-pen style grade stamp, like a mark on a report card. */
export default function Stamp({ grade, size = "md", animate = false }) {
  return (
    <span
      className={`stamp stamp-${grade} stamp-${size}${animate ? " stamp-animate" : ""}`}
      role="img"
      aria-label={`Grade ${grade}: ${GRADE_NOTE[grade]}`}
      title={GRADE_NOTE[grade]}
    >
      {grade}
    </span>
  );
}

export { GRADE_NOTE };
