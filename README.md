# Student Feedback & Analysis System (AI Subject Project)

Students give a **rating (1-5) + comment** for a teacher/subject. The system uses NLP + ML to:
1. classify each comment as **positive / neutral / negative** (English + Hinglish),
2. tag the **topic** (Teaching, Labs, Exams, Course Content, Behaviour),
3. produce **teacher-wise / subject-wise / topic-wise analysis** and a dashboard.

## Run it (3 commands)
```bash
python -m venv venv && venv\Scripts\activate        # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python src/run_pipeline.py                          # builds data, trains model, makes charts + reports
streamlit run app.py                                # opens the dashboard
```

## Project structure
```
data/        feedback.csv (450 comments), feedback_clean.csv (cleaned + topic + prediction)
src/         config, generate_dataset, preprocess, train_model, topics, analysis, predict, visualize, run_pipeline
models/      sentiment_model.pkl (TF-IDF + Logistic Regression)
outputs/     charts (.png), metrics, teacher/subject/topic reports (.csv)
app.py       Streamlit dashboard + live comment predictor
```

## Task -> file mapping
| Task | What | File |
|---|---|---|
| T2 | Dataset (450 rows, 5 teachers, 4 subjects) | `src/generate_dataset.py` |
| T3 | Cleaning, stopwords, lemmatization, labels from rating | `src/preprocess.py` |
| T4 | TF-IDF + Naive Bayes / Logistic Regression + VADER baseline, evaluation | `src/train_model.py` |
| T5 | Keyword-based topic extraction | `src/topics.py` |
| T6 | Teacher/subject/topic analysis, top praises/complaints, mismatches, auto summary | `src/analysis.py` |
| T7 | Pie, bar, stacked bar, word cloud, heatmap, trend charts | `src/visualize.py` |
| T8 | Dashboard + "try a comment" | `app.py`, `src/predict.py` |

## Results (test set, 90 comments)
| Model | Accuracy | Macro F1 |
|---|---|---|
| Naive Bayes | 0.867 | 0.824 |
| **Logistic Regression** | **0.878** | **0.835** |
| VADER (no training) | 0.656 | 0.528 |

VADER is English-only, so it struggles with Hinglish ("samajh nahi aata") - this is why training our own model is better.

## Limitations (write in report)
- Dataset is **synthetic** (template-based), so accuracy is higher than it would be on real student comments. Replace `data/feedback.csv` with real data (same columns) and re-run the pipeline.
- Sarcasm and long mixed-sentiment comments are hard for TF-IDF models.
- Labels come from the rating (>=4 positive, 3 neutral, <=2 negative); ~6% of rows have intentionally mismatched ratings to test the mismatch analysis.
- Topic tagging is keyword based (one topic per comment).

## Future scope
Transformer model (e.g. IndicBERT / multilingual BERT), multi-label topics, LDA topic modelling, login + database (MySQL/Supabase) for live feedback collection, email alerts for low-rated teachers.
