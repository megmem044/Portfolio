"""Reviewer queue retaining both system and human decisions."""
import streamlit as st
from src.config import DATABASE_PATH
from src.database import get_evaluation_runs, get_evaluations
from src.models import RunState
from src.review import ReviewDecision, resolve_human_review

st.set_page_config(page_title="Human Review | AnswerTrust")
st.title("Human review")
runs=get_evaluation_runs(DATABASE_PATH,RunState.HUMAN_REVIEW)
evaluations={row["evaluation_id"]:row for row in get_evaluations(DATABASE_PATH)}
st.metric("Awaiting review",len(runs))
if not runs: st.info("No evaluations require review.")
for run in runs:
    record=evaluations.get(run["evaluation_id"],{})
    with st.expander(f'{run["system_decision"]} · {run["run_id"][:8]}',expanded=True):
        st.write("**Question:**",run["question"]); st.write("**Answer:**",run["answer"])
        for claim in record.get("claim_results",[]):
            st.markdown(f'**{claim["label"]}:** {claim["claim"]}')
            for evidence in claim.get("evidence",[]): st.caption(f'{evidence["section"]}: {evidence["passage"]}')
        notes=st.text_area("Reviewer notes",key=f'notes-{run["run_id"]}')
        left,right=st.columns(2)
        if left.button("Approve",key=f'a-{run["run_id"]}',type="primary"):
            resolve_human_review(run["run_id"],ReviewDecision.APPROVE,DATABASE_PATH,notes); st.rerun()
        if right.button("Reject",key=f'r-{run["run_id"]}'):
            resolve_human_review(run["run_id"],ReviewDecision.REJECT,DATABASE_PATH,notes); st.rerun()
