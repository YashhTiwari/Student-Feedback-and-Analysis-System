"""
One command to run everything:  python src/run_pipeline.py
dataset -> preprocess -> topics -> train -> predict on all rows -> analysis tables -> charts
"""
import joblib
import pandas as pd

import analysis as A
import generate_dataset
import preprocess
import train_model
import visualize
from config import CLEAN_CSV, MODEL_PATH, OUT_DIR, RAW_CSV
from topics import add_topics


def main():
    if not RAW_CSV.exists():
        generate_dataset.generate().to_csv(RAW_CSV, index=False)
        print("Dataset generated.")

    df = preprocess.run()
    add_topics(df).to_csv(CLEAN_CSV, index=False)
    train_model.main()

    df = pd.read_csv(CLEAN_CSV)
    model = joblib.load(MODEL_PATH)
    df["predicted_sentiment"] = model.predict(df["clean_comment"])
    df.to_csv(CLEAN_CSV, index=False)

    A.teacher_report(df).to_csv(OUT_DIR / "teacher_report.csv")
    A.subject_report(df).to_csv(OUT_DIR / "subject_report.csv")
    A.topic_complaints(df).to_csv(OUT_DIR / "topic_complaints.csv")
    A.mismatches(df).to_csv(OUT_DIR / "rating_vs_sentiment_mismatch.csv", index=False)
    A.top_issues(df).to_csv(OUT_DIR / "top_complaints.csv", index=False)
    A.top_praises(df).to_csv(OUT_DIR / "top_praises.csv", index=False)
    with open(OUT_DIR / "teacher_summaries.txt", "w") as f:
        for t in sorted(df["teacher"].unique()):
            f.write(A.teacher_summary_text(df, t) + "\n")

    visualize.run_all(df)
    print("\nPipeline complete. Now run:  streamlit run app.py")


if __name__ == "__main__":
    main()
