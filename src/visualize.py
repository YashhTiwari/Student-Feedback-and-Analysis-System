"""T7: All charts. Each function returns a matplotlib Figure (used by app.py) and run_all() saves PNGs."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

from analysis import monthly_trend, teacher_report, teacher_topic_matrix
from config import OUT_DIR
from preprocess import STOPWORDS

COLORS = {"positive": "#55A868", "neutral": "#F2C14E", "negative": "#C44E52"}


def sentiment_pie(df):
    counts = df["sentiment"].value_counts().reindex(["positive", "neutral", "negative"]).fillna(0)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%", colors=[COLORS[k] for k in counts.index], startangle=90)
    ax.set_title("Overall Sentiment Split")
    return fig


def teacher_bar(df):
    rep = teacher_report(df)
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(x=rep.index, y=rep["avg_rating"], hue=rep.index, palette="viridis", legend=False, ax=ax)
    ax.set_ylim(0, 5)
    ax.set_ylabel("Average rating")
    ax.set_xlabel("")
    ax.set_title("Teacher-wise Average Rating")
    for i, v in enumerate(rep["avg_rating"]):
        ax.text(i, v + 0.05, f"{v:.2f}", ha="center")
    plt.setp(ax.get_xticklabels(), rotation=15)
    fig.tight_layout()
    return fig


def teacher_sentiment_stacked(df):
    rep = teacher_report(df)[["positive", "neutral", "negative"]]
    fig, ax = plt.subplots(figsize=(7, 4))
    rep.plot(kind="bar", stacked=True, color=[COLORS[c] for c in rep.columns], ax=ax)
    ax.set_ylabel("% of comments")
    ax.set_xlabel("")
    ax.set_title("Sentiment Breakdown per Teacher")
    plt.setp(ax.get_xticklabels(), rotation=15)
    fig.tight_layout()
    return fig


def wordcloud_fig(df, sentiment=None):
    d = df if sentiment is None else df[df["sentiment"] == sentiment]
    text = " ".join(d["clean_comment"])
    wc = WordCloud(width=800, height=400, background_color="white", stopwords=STOPWORDS | {"bahut", "very", "hope", "thing", "change", "need", "improvement", "please", "fix", "overall", "chal", "mazaa", "keep", "highly", "recommend", "okay"},
                   colormap="viridis" if sentiment is None else ("Greens" if sentiment == "positive" else "Reds"))
    wc.generate(text)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Word Cloud" + (f" - {sentiment}" if sentiment else ""))
    return fig


def heatmap_fig(df):
    m = teacher_topic_matrix(df, "negative")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(m, annot=True, fmt=".0f", cmap="Reds", ax=ax, cbar_kws={"label": "% negative"})
    ax.set_title("Teacher x Topic: % Negative Feedback")
    ax.set_ylabel("")
    ax.set_xlabel("")
    fig.tight_layout()
    return fig


def trend_fig(df):
    t = monthly_trend(df)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t.index, t["avg_rating"], marker="o", color="#4C72B0")
    ax.set_ylim(0, 5)
    ax.set_ylabel("Average rating")
    ax.set_title("Monthly Rating Trend")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def run_all(df):
    charts = {
        "sentiment_pie": sentiment_pie(df),
        "teacher_rating_bar": teacher_bar(df),
        "teacher_sentiment_stacked": teacher_sentiment_stacked(df),
        "wordcloud_all": wordcloud_fig(df),
        "wordcloud_negative": wordcloud_fig(df, "negative"),
        "teacher_topic_heatmap": heatmap_fig(df),
        "monthly_trend": trend_fig(df),
    }
    for name, fig in charts.items():
        fig.savefig(OUT_DIR / f"{name}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
    print(f"Saved {len(charts)} charts -> {OUT_DIR}")
