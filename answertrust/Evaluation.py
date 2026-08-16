"""AnswerTrust: research-grounded answer evaluation UI."""

import streamlit as st

from src.api_client import AnswerTrustAPIClient
from src.models import EvaluationInput
from src.ui import apply_theme, evidence_block, hero, verdict

st.set_page_config(page_title="AnswerTrust", page_icon="A", layout="wide", initial_sidebar_state="expanded")
apply_theme()
hero("Research-grounded AI evaluation", "Know what the paper actually supports.", "AnswerTrust decomposes generated answers into claims, retrieves evidence from the supplied research, and flags contradictions, overstatement, and missing support.", tone="lemon")


st.markdown('<div class="at-kicker">New evaluation</div>', unsafe_allow_html=True)
st.subheader("Check an AI answer")
with st.form("evaluation"):
    st.markdown('<div class="at-section-title"><span class="at-step">1</span>Frame the research question</div>', unsafe_allow_html=True)
    question = st.text_input("Research question", placeholder="What did the study find about the treatment?")
    paper_column, answer_column = st.columns([1.25, 1])
    with paper_column:
        st.markdown('<div class="at-section-title"><span class="at-step">2</span>Add the trusted paper evidence</div>', unsafe_allow_html=True)
        paper = st.text_area("Paper or selected text", height=290, placeholder="METHODS\n...\n\nRESULTS\n...\n\nLIMITATIONS\n...")
    with answer_column:
        st.markdown('<div class="at-section-title"><span class="at-step">3</span>Add the generated answer</div>', unsafe_allow_html=True)
        answer = st.text_area("AI-generated answer", height=290, placeholder="Paste the answer that should be checked against the paper.")
    st.caption("The evaluation is sent to the local AnswerTrust API.")
    submitted = st.form_submit_button("Evaluate claims", type="primary", use_container_width=True)

if submitted:
    try:
        with st.spinner("Extracting claims and checking academic evidence..."):
            result = AnswerTrustAPIClient().create_evaluation(
                EvaluationInput(question, paper, answer)
            )
            run_id = result.evaluation_id
    except Exception:
        st.error(
            "The evaluation API is unavailable. Start FastAPI and try again."
        )
    else:
        verdict(result.final_decision.value, result.overall_score, result.recommended_action, f"Run {run_id[:8]} · {result.explanation} · {result.total_latency_ms} ms")
        st.subheader("Claim audit")
        for index, claim in enumerate(result.claim_results, 1):
            with st.expander(f"Claim {index} · {claim.label.value.replace('_', ' ')}", expanded=True):
                st.markdown(f'<div class="at-claim">{claim.claim}</div>', unsafe_allow_html=True)
                st.write(claim.explanation)
                if claim.nli_label:
                    st.caption(f"NLI prediction: {claim.nli_label} · confidence {claim.nli_confidence:.0%}")
                if claim.failure_types:
                    names = ["NLI contradiction requires confirmation" if item == "NLI_ONLY_CONTRADICTION" else item.replace("_", " ").title() for item in claim.failure_types]
                    st.warning(" · ".join(names))
                st.markdown("**Evidence used**")
                for evidence in claim.evidence: evidence_block(evidence.section, evidence.similarity, evidence.passage)

st.markdown("---")
nav_left, nav_right = st.columns(2)
if nav_left.button("Review flagged evaluations →", use_container_width=True): st.switch_page("pages/1_Human_Review.py")
if nav_right.button("View measured benchmarks →", use_container_width=True): st.switch_page("pages/2_Benchmark.py")
