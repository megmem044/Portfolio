"""Streamlit entry point for AnswerTrust."""

import streamlit as st

from src import database
from src.config import DATABASE_PATH
from src.evaluator import evaluate_answer
from src.models import Decision, EvaluationInput, EvaluationResult
from src.transformer_evaluator import (
    LocalTransformerEvaluator,
    PROMPT_VERSIONS,
)


st.set_page_config(
    page_title="AnswerTrust",
    page_icon="✅",
    layout="wide",
)


@st.cache_resource
def get_transformer_evaluator() -> LocalTransformerEvaluator:
    """Create one lazy local-model wrapper per Streamlit process."""
    return LocalTransformerEvaluator()


def show_decision(decision: Decision) -> None:
    """Display the publication decision prominently."""

    messages = {
        Decision.PUBLISH: "PUBLISH — This answer meets the current quality rules.",
        Decision.REVIEW: "REVIEW — Check the concerns before publishing.",
        Decision.REJECT: "REJECT — This answer requires substantial revision.",
    }

    if decision == Decision.PUBLISH:
        st.success(messages[decision])
    elif decision == Decision.REVIEW:
        st.warning(messages[decision])
    else:
        st.error(messages[decision])


def show_result(result: EvaluationResult) -> None:
    """Display a completed AnswerTrust evaluation."""

    if result.dimension_scores[0].name == "Validation":
        for concern in result.dimension_scores[0].concerns:
            st.error(concern)
        return

    show_decision(result.final_decision)

    score_column, latency_column = st.columns(2)

    with score_column:
        st.metric("Overall score", f"{result.overall_score}/100")

    with latency_column:
        st.metric("Evaluation time", f"{result.total_latency_ms} ms")

    st.subheader("Quality scores")

    for dimension in result.dimension_scores:
        st.write(f"**{dimension.name}: {dimension.score}/100**")
        st.progress(dimension.score / 100)
        st.caption(dimension.explanation)

        for concern in dimension.concerns:
            st.warning(concern)

    st.subheader("Summary")
    st.write(f"**Main concern:** {result.main_concern}")
    st.write(f"**Recommended action:** {result.recommended_action}")

    if result.model_status == "generated":
        st.subheader("Local transformer explanation")
        st.write(result.explanation)
        st.caption(
            f"Prompt: {result.prompt_version} · "
            f"Transformer latency: {result.transformer_latency_ms} ms"
        )
    elif result.model_status != "not_used":
        st.info(
            "The optional local transformer was unavailable or returned an "
            "invalid response. The deterministic result above remains valid."
        )


st.title("AnswerTrust")
st.write(
    "Evaluate whether an AI-generated answer is supported, relevant, "
    "complete, clear, and appropriately cautious."
)

st.info(
    "AnswerTrust evaluates an answer against the reference supplied below. "
    "It does not verify universal factual truth."
)

with st.form("evaluation_form"):
    question = st.text_area(
        "Question",
        placeholder="Enter the question being answered.",
        height=120,
    )

    reference = st.text_area(
        "Reference information",
        placeholder="Enter the information that should support the answer.",
        height=180,
    )

    answer = st.text_area(
        "AI-generated answer",
        placeholder="Enter the answer you want to evaluate.",
        height=180,
    )

    use_transformer = st.checkbox(
        "Use optional local transformer explanation",
        help=(
            "Requires google/flan-t5-small in the local Hugging Face cache. "
            "The model never overrides AnswerTrust's official decision."
        ),
    )
    prompt_version = st.selectbox(
        "Transformer prompt",
        options=PROMPT_VERSIONS,
        disabled=not use_transformer,
    )

    submitted = st.form_submit_button(
        "Evaluate Answer",
        type="primary",
        use_container_width=True,
    )

if submitted:
    evaluation_input = EvaluationInput(
        question=question,
        reference=reference,
        answer=answer,
        prompt_version=prompt_version,
    )

    transformer_evaluator = (
        get_transformer_evaluator() if use_transformer else None
    )
    evaluation_result = evaluate_answer(
        evaluation_input,
        transformer_evaluator=transformer_evaluator,
    )
    show_result(evaluation_result)

    is_valid_evaluation = (
        evaluation_result.dimension_scores[0].name != "Validation"
    )
    if is_valid_evaluation:
        try:
            database.save_evaluation(
                evaluation_input,
                evaluation_result,
                DATABASE_PATH,
            )
            st.caption("Evaluation saved to local history.")
        except Exception:
            st.warning(
                "The evaluation completed, but it could not be saved to history."
            )
