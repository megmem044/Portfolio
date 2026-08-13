"""Human-review workspace retaining system and reviewer decisions."""
import streamlit as st
from src.config import DATABASE_PATH
from src.database import get_evaluation_runs, get_evaluations
from src.models import RunState
from src.review import ReviewDecision, resolve_human_review
from src.ui import apply_theme, evidence_block, hero

st.set_page_config(page_title="Human Review | AnswerTrust", page_icon="A", layout="wide")
apply_theme()
hero("Human-in-the-loop safety", "Review the edge cases.", "Resolve claims that need judgment while preserving the original system decision, evidence, reviewer notes, and final outcome.", tone="lavender")
runs = get_evaluation_runs(DATABASE_PATH, RunState.HUMAN_REVIEW)
evaluations = {row["evaluation_id"]: row for row in get_evaluations(DATABASE_PATH)}
left, right, _ = st.columns([1, 1, 2]); left.metric("Awaiting review", len(runs)); right.metric("Workflow", "Local SQLite")
if not runs: st.success("Review queue clear. No evaluations currently require human judgment.")
for run in runs:
    record = evaluations.get(run["evaluation_id"], {})
    with st.expander(f'REVIEW · Run {run["run_id"][:8]}', expanded=True):
        question_column, answer_column = st.columns(2)
        with question_column: st.caption("RESEARCH QUESTION"); st.write(run["question"])
        with answer_column: st.caption("AI-GENERATED ANSWER"); st.write(run["answer"])
        st.markdown("---")
        for index, claim in enumerate(record.get("claim_results", []), 1):
            st.markdown(f'**Claim {index} · {claim["label"].replace("_", " ")}**'); st.write(claim["claim"])
            if claim.get("nli_label"): st.caption(f'NLI: {claim["nli_label"]} · confidence {claim["nli_confidence"]:.0%}')
            for evidence in claim.get("evidence", []): evidence_block(evidence["section"], evidence["similarity"], evidence["passage"])
        notes = st.text_area("Reviewer notes", key=f'notes-{run["run_id"]}', placeholder="Explain why the evaluation should be approved or rejected...")
        approve, reject = st.columns(2)
        if approve.button("Approve evaluation", key=f'a-{run["run_id"]}', type="primary", use_container_width=True):
            resolve_human_review(run["run_id"], ReviewDecision.APPROVE, DATABASE_PATH, notes); st.rerun()
        if reject.button("Reject evaluation", key=f'r-{run["run_id"]}', use_container_width=True):
            resolve_human_review(run["run_id"], ReviewDecision.REJECT, DATABASE_PATH, notes); st.rerun()
