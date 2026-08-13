"""AnswerTrust: research-grounded answer evaluation UI."""

import streamlit as st

from src.config import DATABASE_PATH
from src.models import EvaluationInput
from src.nli import NLIClassifier
from src.semantic import SemanticMatcher
from src.ui import apply_theme, evidence_block, hero, verdict
from src.workflow import execute_evaluation_run

st.set_page_config(page_title="AnswerTrust", page_icon="A", layout="wide", initial_sidebar_state="expanded")
apply_theme()
hero("Research-grounded AI evaluation", "Know what the paper actually supports.", "AnswerTrust decomposes generated answers into claims, retrieves evidence from the supplied research, and flags contradictions, overstatement, and missing support.", tone="lemon")


@st.cache_resource
def load_semantic_matcher() -> SemanticMatcher:
    return SemanticMatcher()


@st.cache_resource
def load_nli_classifier() -> NLIClassifier:
    return NLIClassifier()


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
    with st.expander("Evaluation engines", expanded=False):
        ml_left, ml_right = st.columns(2)
        use_semantic = ml_left.checkbox("Semantic evidence retrieval", value=True, help="MiniLM matches paraphrased claims to evidence.")
        use_nli = ml_right.checkbox("Entailment and contradiction model", value=True, help="Confidence-gated NLI classification with deterministic fallback.")
        st.caption("Models run locally. AnswerTrust never searches the web or adds outside evidence.")
    submitted = st.form_submit_button("Evaluate claims", type="primary", use_container_width=True)

if submitted:
    matcher = None
    nli_classifier = None
    if use_semantic:
        try: matcher = load_semantic_matcher()
        except Exception: st.warning("Semantic model unavailable. Continuing with keyword evidence matching.")
    if use_nli:
        try: nli_classifier = load_nli_classifier()
        except Exception: st.warning("NLI model unavailable. Continuing with deterministic claim labels.")
    try:
        with st.spinner("Extracting claims and checking academic evidence..."):
            run_id, result = execute_evaluation_run(EvaluationInput(question, paper, answer), DATABASE_PATH, semantic_matcher=matcher, nli_classifier=nli_classifier)
    except ValueError as error: st.error(str(error))
    except Exception as error: st.error(f"Evaluation failed after automatic retries: {error}")
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
