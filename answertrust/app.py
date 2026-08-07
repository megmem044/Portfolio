"""Streamlit entry point for AnswerTrust."""

import streamlit as st

from src.evaluator import evaluate_answer
from src.models import Decision, EvaluationInput, EvaluationResult


st.set_page_config(
    page_title="AnswerTrust",
    page_icon="✅",
    layout="wide",
)


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
    )

    evaluation_result = evaluate_answer(evaluation_input)
    show_result(evaluation_result)