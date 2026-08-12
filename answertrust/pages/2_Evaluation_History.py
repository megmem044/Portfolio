"""Streamlit page for browsing locally saved evaluations."""

from datetime import datetime

import streamlit as st

from src.config import DATABASE_PATH
from src.database import get_evaluation_runs, get_evaluations
from src.models import Decision
from src.ui import apply_workspace_theme


st.set_page_config(
    page_title="Evaluation History | AnswerTrust",
    page_icon="📋",
    layout="wide",
)

apply_workspace_theme()

st.title("Evaluation History")
st.write(
    "Review evaluations saved on this computer. History remains local in "
    "the AnswerTrust SQLite database."
)

decision_filter = st.selectbox(
    "Decision",
    options=["All", *[decision.value for decision in Decision]],
)

selected_decision = (
    None if decision_filter == "All" else Decision(decision_filter)
)

try:
    evaluations = get_evaluations(DATABASE_PATH, selected_decision)
except Exception:
    st.error("Evaluation history could not be loaded.")
    evaluations = []

try:
    runs = get_evaluation_runs(DATABASE_PATH)
except Exception:
    st.warning("Workflow states could not be loaded.")
    runs = []

run_by_evaluation_id = {
    run["evaluation_id"]: run
    for run in runs
    if run["evaluation_id"] is not None
}

FAILURE_LABELS = {
    "MODEL_UNAVAILABLE": "Model unavailable",
    "MODEL_TIMEOUT": "Model timeout",
    "INVALID_OUTPUT": "Invalid output",
    "LOW_CONFIDENCE": "Low confidence",
    "INSUFFICIENT_SUPPORT": "Insufficient support",
    "EVALUATION_ERROR": "Evaluation error",
}

if not evaluations:
    st.info("No saved evaluations match this filter.")

for evaluation in evaluations:
    timestamp = datetime.fromisoformat(evaluation["timestamp"])
    run = run_by_evaluation_id.get(evaluation["evaluation_id"])
    workflow_state = run["state"] if run else "LEGACY"
    heading = (
        f'{evaluation["final_decision"]} · '
        f'{evaluation["overall_score"]}/100 · '
        f'{timestamp:%Y-%m-%d %H:%M}'
    )

    with st.expander(heading):
        st.write(f"**Workflow state:** {workflow_state}")
        if run:
            st.caption(f'Run ID: {run["run_id"]}')
            failure_type = run.get("failure_type")
            failure_message = run.get("failure_message")
            if failure_type == "MODEL_UNAVAILABLE":
                st.info(
                    "**Deterministic fallback used** — the optional model "
                    "was unavailable, so the rule-based evaluation "
                    "completed the run."
                )
            elif failure_type:
                failure_label = FAILURE_LABELS.get(
                    failure_type,
                    failure_type.replace("_", " ").title(),
                )
                st.warning(f"**Run classification:** {failure_label}")

            if failure_message:
                st.write(f"**Classification reason:** {failure_message}")
        else:
            st.caption(
                "This evaluation predates persistent workflow runs."
            )
        st.write(f'**Question:** {evaluation["question"]}')
        st.write(f'**Reference:** {evaluation["reference"]}')
        st.write(f'**Answer:** {evaluation["answer"]}')
        st.write(f'**Main concern:** {evaluation["main_concern"]}')
        st.write(
            f'**Recommended action:** {evaluation["recommended_action"]}'
        )

        st.subheader("Dimension scores")
        for dimension in evaluation["dimension_scores"]:
            st.write(
                f'**{dimension["name"]}: {dimension["score"]}/100**'
            )
            st.caption(dimension["explanation"])
