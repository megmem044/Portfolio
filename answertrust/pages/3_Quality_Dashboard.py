"""Streamlit dashboard for local quality and experiment metrics."""

from collections import Counter

import pandas as pd
import streamlit as st

from src import dashboard, database
from src.config import DATABASE_PATH, EXPERIMENT_RESULTS_PATH


st.set_page_config(
    page_title="Quality Dashboard | AnswerTrust",
    page_icon="📊",
    layout="wide",
)

st.title("Quality Dashboard")
st.write(
    "Monitor locally saved evaluations and measured offline experiment results."
)

st.header("Local evaluation history")
try:
    history_records = database.get_evaluations(DATABASE_PATH)
    history = dashboard.summarize_history(history_records)
except Exception:
    st.error("Local evaluation metrics could not be loaded.")
    history_records = []
    history = dashboard.summarize_history([])

history_columns = st.columns(3)
history_columns[0].metric("Saved evaluations", history["total_evaluations"])
history_columns[1].metric("Average score", f'{history["average_score"]}/100')
history_columns[2].metric(
    "Average latency",
    f'{history["average_latency_ms"]} ms',
)

if history_records:
    decision_frame = pd.DataFrame(
        {
            "Decision": list(history["decision_counts"].keys()),
            "Count": list(history["decision_counts"].values()),
        }
    ).set_index("Decision")
    st.subheader("Saved decisions")
    st.bar_chart(decision_frame)

    st.subheader("Common concerns")
    if history["common_concerns"]:
        for concern, count in history["common_concerns"]:
            st.write(f"- {concern} ({count})")
    else:
        st.info("No concerns have been recorded in local history.")
else:
    st.info("Submit evaluations from the main page to populate local metrics.")

st.header("Offline experiment")
try:
    experiment_rows = dashboard.load_experiment_results(
        EXPERIMENT_RESULTS_PATH
    )
except FileNotFoundError:
    experiment_rows = []
    st.info(
        "No experiment results are available. Run "
        "`python -m src.experiments` to generate them."
    )
except Exception:
    experiment_rows = []
    st.error("Experiment results could not be loaded.")

if experiment_rows:
    experiment = dashboard.summarize_experiment(experiment_rows)
    experiment_columns = st.columns(4)
    experiment_columns[0].metric(
        "Decision accuracy",
        f'{experiment["decision_accuracy_pct"]}%',
    )
    experiment_columns[1].metric(
        "False-publish rate",
        f'{experiment["false_publish_rate_pct"]}%',
    )
    experiment_columns[2].metric(
        "Unsupported detection",
        f'{experiment["unsupported_detection_rate_pct"]}%',
    )
    experiment_columns[3].metric(
        "Review rate",
        f'{experiment["review_rate_pct"]}%',
    )

    actual_counts = Counter(
        row["actual_decision"] for row in experiment_rows
    )
    experiment_frame = pd.DataFrame(
        {
            "Decision": list(actual_counts.keys()),
            "Count": list(actual_counts.values()),
        }
    ).set_index("Decision")
    st.subheader("Experiment decisions")
    st.bar_chart(experiment_frame)
    st.caption(
        f'Measured on {experiment["total_examples"]} self-authored examples. '
        "Results describe this dataset and do not guarantee general performance."
    )
