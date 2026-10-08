"""
T6: Analysis engine. All functions take the cleaned dataframe (with topic + predicted sentiment).
"""
from collections import Counter

import pandas as pd

from preprocess import STOPWORDS

SENTS = ["positive", "neutral", "negative"]


def sentiment_pct(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """% of positive/neutral/negative comments per group + avg rating + count."""
    pct = pd.crosstab(df[by], df["sentiment"], normalize="index").reindex(columns=SENTS, fill_value=0) * 100
    out = pct.round(1)
    out["avg_rating"] = df.groupby(by)["rating"].mean().round(2)
    out["responses"] = df.groupby(by).size()
    return out.sort_values("avg_rating", ascending=False)


def teacher_report(df):
    return sentiment_pct(df, "teacher")


def subject_report(df):
    return sentiment_pct(df, "subject")


def topic_complaints(df: pd.DataFrame) -> pd.DataFrame:
    """For each topic: % negative comments (higher = bigger problem area)."""
    out = sentiment_pct(df, "topic")
    return out.sort_values("negative", ascending=False)


def teacher_topic_matrix(df: pd.DataFrame, value="negative") -> pd.DataFrame:
    """% of `value` sentiment for each teacher x topic (used for heatmap)."""
    pivot = df.pivot_table(index="teacher", columns="topic", values="sentiment",
                           aggfunc=lambda s: (s == value).mean() * 100)
    return pivot.round(1)


def top_words(df: pd.DataFrame, sentiment: str, n: int = 10) -> pd.DataFrame:
    words = " ".join(df.loc[df["sentiment"] == sentiment, "clean_comment"]).split()
    skip = STOPWORDS | {"bahut", "very", "overall", "highly", "hope", "thing", "change", "need", "improvement",
                        "please", "fix", "chal", "mazaa", "keep", "disappointing", "recommend", "okay"}
    counts = Counter(w for w in words if w not in skip and len(w) > 2)
    return pd.DataFrame(counts.most_common(n), columns=["word", "count"])


def top_issues(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Most repeated negative comments (base sentence only) -> the 'top complaints' list."""
    neg = df[df["sentiment"] == "negative"]["comment"].str.split(". ", regex=False).str[0].str.strip(". ")
    return neg.value_counts().head(n).rename_axis("complaint").reset_index(name="count")


def top_praises(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    pos = df[df["sentiment"] == "positive"]["comment"].str.split(". ", regex=False).str[0].str.strip(". ")
    return pos.value_counts().head(n).rename_axis("praise").reset_index(name="count")


def mismatches(df: pd.DataFrame) -> pd.DataFrame:
    """Rows where the rating disagrees with the sentiment predicted from the comment text."""
    rating_sent = df["rating"].apply(lambda r: "positive" if r >= 4 else "neutral" if r == 3 else "negative")
    m = df[(df["predicted_sentiment"] != rating_sent)].copy()
    m["rating_says"] = rating_sent[m.index]
    return m[["teacher", "rating", "rating_says", "predicted_sentiment", "comment"]]


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["month"] = pd.to_datetime(d["date"]).dt.to_period("M").astype(str)
    return d.groupby("month").agg(avg_rating=("rating", "mean"), responses=("rating", "size")).round(2)


def teacher_summary_text(df: pd.DataFrame, teacher: str) -> str:
    """Auto-generated one-paragraph summary for a teacher."""
    t = df[df["teacher"] == teacher]
    if t.empty:
        return "No data."
    pos = (t["sentiment"] == "positive").mean() * 100
    neg = (t["sentiment"] == "negative").mean() * 100
    tp = t.groupby("topic")["sentiment"].apply(lambda s: (s == "positive").mean() * 100)
    tn = t.groupby("topic")["sentiment"].apply(lambda s: (s == "negative").mean() * 100)
    weakness = tn.idxmax()
    strength = tp.drop(index=weakness, errors="ignore").idxmax() if len(tp) > 1 else tp.idxmax()
    verdict = "Excellent" if pos >= 65 else "Good" if pos >= 45 else "Needs attention" if neg < 50 else "Needs urgent improvement"
    return (f"{teacher} ({t['subject'].iloc[0]}): {verdict}. {pos:.0f}% positive, {neg:.0f}% negative "
            f"from {len(t)} responses (avg rating {t['rating'].mean():.2f}/5). "
            f"Strongest area: {strength}. Weakest area: {weakness} ({tn.max():.0f}% negative).")
