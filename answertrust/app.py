"""AnswerTrust: research-grounded answer evaluation UI."""

import streamlit as st

from src.config import DATABASE_PATH
from src.models import EvaluationInput
from src.semantic import SemanticMatcher
from src.workflow import execute_evaluation_run

st.set_page_config(page_title="AnswerTrust", page_icon="✓", layout="wide")
st.title("AnswerTrust")
st.caption("Claim-level checks against one supplied academic paper. No web search, RAG, or external knowledge.")


@st.cache_resource
def load_semantic_matcher() -> SemanticMatcher:
    """Load the local embedding model once per Streamlit process."""
    return SemanticMatcher()

with st.form("evaluation"):
    question = st.text_input("Research question", placeholder="What did the study find about the treatment?")
    paper = st.text_area("Paper or selected paper text", height=300, placeholder="METHODS\n...\n\nRESULTS\n...\n\nLIMITATIONS\n...")
    answer = st.text_area("AI-generated answer", height=150)
    use_semantic = st.checkbox(
        "Use ML semantic evidence matching",
        value=True,
        help="Uses the local all-MiniLM-L6-v2 model to match paraphrased claims.",
    )
    submitted = st.form_submit_button("Evaluate answer", type="primary")

if submitted:
    matcher = None
    if use_semantic:
        try:
            matcher = load_semantic_matcher()
        except Exception:
            st.warning(
                "The local embedding model could not be loaded. "
                "AnswerTrust continued with keyword evidence matching."
            )
    try:
        run_id, result = execute_evaluation_run(
            EvaluationInput(question, paper, answer),
            DATABASE_PATH,
            semantic_matcher=matcher,
        )
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        st.error(f"Evaluation failed after automatic retries: {error}")
    else:
        st.subheader(f"{result.final_decision.value} · {result.overall_score}/100")
        st.write(result.recommended_action)
        st.caption(f"Run {run_id} · {result.explanation}")
        for index, claim in enumerate(result.claim_results, 1):
            with st.expander(f"Claim {index}: {claim.label.value}", expanded=True):
                st.write(claim.claim)
                st.write(claim.explanation)
                if claim.failure_types:
                    st.warning("Failure types: " + ", ".join(claim.failure_types))
                for evidence in claim.evidence:
                    st.markdown(f"**{evidence.section}** · match {evidence.similarity:.0%}")
                    st.info(evidence.passage)

st.divider()
review_column, benchmark_column = st.columns(2)
if review_column.button("Open human review queue", use_container_width=True):
    st.switch_page("pages/1_Human_Review.py")
if benchmark_column.button("Open benchmark results", use_container_width=True):
    st.switch_page("pages/2_Benchmark.py")
