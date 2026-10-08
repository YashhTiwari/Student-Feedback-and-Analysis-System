"""
T8: Streamlit app.   Run:  streamlit run app.py
Pages: Dashboard | Teacher Report | Try a Comment | Model Performance | Raw Data
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

import analysis as A  # noqa: E402
import visualize as V  # noqa: E402
from config import CLEAN_CSV, MODEL_PATH, OUT_DIR  # noqa: E402
from predict import predict_comment  # noqa: E402

st.set_page_config(page_title="Student Feedback Analysis", page_icon="📊", layout="wide")


@st.cache_data
def load():
    return pd.read_csv(CLEAN_CSV)


if not CLEAN_CSV.exists() or not MODEL_PATH.exists():
    st.error("Data/model not found. Run `python src/run_pipeline.py` first.")
    st.stop()

df = load()

st.sidebar.title("📊 Feedback Analysis")
page = st.sidebar.radio("Go to", ["Dashboard", "Teacher Report", "Try a Comment", "Model Performance", "Raw Data"])
subjects = ["All"] + sorted(df["subject"].unique())
subject_filter = st.sidebar.selectbox("Filter by subject", subjects)
view = df if subject_filter == "All" else df[df["subject"] == subject_filter]

if page == "Dashboard":
    st.title("Student Feedback & Analysis System")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total responses", len(view))
    c2.metric("Average rating", f"{view['rating'].mean():.2f} / 5")
    c3.metric("Positive", f"{(view['sentiment'] == 'positive').mean() * 100:.0f}%")
    c4.metric("Negative", f"{(view['sentiment'] == 'negative').mean() * 100:.0f}%")

    a, b = st.columns(2)
    a.pyplot(V.sentiment_pie(view))
    b.pyplot(V.teacher_bar(view))
    a.pyplot(V.teacher_sentiment_stacked(view))
    b.pyplot(V.trend_fig(view))
    st.pyplot(V.heatmap_fig(view))

    st.subheader("Where are students unhappy? (by topic)")
    st.dataframe(A.topic_complaints(view), use_container_width=True)

    x, y = st.columns(2)
    x.subheader("Top complaints")
    x.dataframe(A.top_issues(view), use_container_width=True, hide_index=True)
    y.subheader("Top praises")
    y.dataframe(A.top_praises(view), use_container_width=True, hide_index=True)

    st.subheader("Word clouds")
    w1, w2 = st.columns(2)
    w1.pyplot(V.wordcloud_fig(view, "positive"))
    w2.pyplot(V.wordcloud_fig(view, "negative"))

elif page == "Teacher Report":
    st.title("Teacher-wise Report")
    teacher = st.selectbox("Select teacher", sorted(df["teacher"].unique()))
    t = df[df["teacher"] == teacher]
    st.info(A.teacher_summary_text(df, teacher))
    c1, c2, c3 = st.columns(3)
    c1.metric("Responses", len(t))
    c2.metric("Avg rating", f"{t['rating'].mean():.2f}")
    c3.metric("Positive %", f"{(t['sentiment'] == 'positive').mean() * 100:.0f}%")
    st.subheader("Sentiment by topic")
    st.dataframe(A.sentiment_pct(t, "topic"), use_container_width=True)
    st.subheader("Recent negative comments")
    st.dataframe(t[t["sentiment"] == "negative"][["date", "rating", "topic", "comment"]].tail(10),
                 use_container_width=True, hide_index=True)
    st.subheader("Rating vs comment mismatches")
    mm = A.mismatches(t) if "predicted_sentiment" in t else pd.DataFrame()
    st.dataframe(mm, use_container_width=True, hide_index=True)

elif page == "Try a Comment":
    st.title("Try a new comment")
    text = st.text_area("Type a student comment (English / Hinglish)",
                        "Sir ka padhane ka tarika accha hai but lab mein computers kaam nahi karte")
    if st.button("Analyze") and text.strip():
        r = predict_comment(text)
        icon = {"positive": "🟢", "neutral": "🟡", "negative": "🔴"}[r["sentiment"]]
        st.subheader(f"{icon} {r['sentiment'].title()}  ({r['confidence'] * 100:.0f}% confidence)")
        st.write(f"**Topic:** {r['topic']}")
        st.bar_chart(pd.Series(r["probabilities"]))
        with st.expander("Cleaned text (what the model sees)"):
            st.code(r["cleaned"])

elif page == "Model Performance":
    st.title("Model Performance")
    st.dataframe(pd.read_csv(OUT_DIR / "model_comparison.csv", index_col=0), use_container_width=True)
    a, b = st.columns(2)
    a.image(str(OUT_DIR / "confusion_matrix.png"))
    b.image(str(OUT_DIR / "model_comparison.png"))
    st.text((OUT_DIR / "classification_report.txt").read_text())

else:
    st.title("Dataset")
    st.dataframe(view, use_container_width=True)
    st.download_button("Download CSV", view.to_csv(index=False), "feedback_clean.csv")
