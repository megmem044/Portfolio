"""Human-review workspace connected to the AnswerTrust API."""

import streamlit as st

from src.api_client import AnswerTrustAPIClient
from src.ui import apply_theme, evidence_block, hero

st.set_page_config(page_title="Human Review | AnswerTrust", page_icon="A", layout="wide")
apply_theme()
hero("Human-in-the-loop safety", "Review the edge cases.", "Resolve claims that need judgment while preserving the original system decision, evidence, reviewer notes, and final outcome.", tone="lavender")

api = AnswerTrustAPIClient()
try:
    items = api.list_review_required()
except Exception:
    st.error("The review API is unavailable. Start FastAPI and refresh this page.")
    items = []

left, right, _ = st.columns([1, 1, 2])
left.metric("Awaiting review", len(items))
right.metric("Workflow", "FastAPI")

if not items:
    st.success("Review queue clear. No evaluations currently require human judgment.")

for item in items:
    result = item["evaluation"]
    evaluation_id = result["evaluation_id"]
    with st.expander(f"REVIEW · Evaluation {evaluation_id[:8]}", expanded=True):
        question_column, answer_column = st.columns(2)
        with question_column:
            st.caption("RESEARCH QUESTION")
            st.write(item["question"])
        with answer_column:
            st.caption("AI-GENERATED ANSWER")
            st.write(item["answer"])
        st.markdown("---")
        for index, claim in enumerate(result["claim_results"], 1):
            label = claim["label"].replace("_", " ")
            st.markdown(f"**Claim {index} · {label}**")
            st.write(claim["claim"])
            for evidence in claim["evidence"]:
                evidence_block(evidence["section"], evidence["similarity"], evidence["passage"])
        notes = st.text_area(
            "Reviewer notes",
            key=f"notes-{evaluation_id}",
            placeholder="Explain why the evaluation should be approved or rejected...",
        )
        approve, reject = st.columns(2)
        notes_missing = len(notes.strip()) < 3
        if approve.button("Approve evaluation", key=f"a-{evaluation_id}", type="primary", use_container_width=True, disabled=notes_missing):
            api.review_evaluation(evaluation_id, "APPROVE", notes)
            st.rerun()
        if reject.button("Reject evaluation", key=f"r-{evaluation_id}", use_container_width=True, disabled=notes_missing):
            api.review_evaluation(evaluation_id, "REJECT", notes)
            st.rerun()
