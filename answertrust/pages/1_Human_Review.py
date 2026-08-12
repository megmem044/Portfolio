"""Streamlit page for resolving runs that require human review."""

import streamlit as st

from src.config import DATABASE_PATH
from src.database import get_evaluation_runs, get_evaluations
from src.models import RunState
from src.review import ReviewDecision, resolve_human_review
from src.ui import apply_workspace_theme


st.set_page_config(
    page_title="Human Review | AnswerTrust",
    page_icon="👤",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at 90% 0%, #fff3dc 0,
                        transparent 25rem), #f7f9fc;
        }
        [data-testid="stHeader"] { background: rgba(247,249,252,.86); }
        .block-container { max-width: 1120px; padding-top: 2.5rem; }
        h1, h2, h3 { color: #172033; letter-spacing: -.025em; }
        div[data-testid="stExpander"] {
            background: rgba(255,255,255,.96);
            border: 1px solid #dfe5ef;
            border-radius: 16px;
            box-shadow: 0 10px 28px rgba(28,39,60,.06);
            overflow: hidden;
        }
        div[data-testid="stMetric"] {
            background: #fff; border: 1px solid #e1e6ef;
            border-radius: 14px; padding: .9rem 1rem;
        }
        div[data-testid="stAlert"] { border-radius: 12px; }
        .review-eyebrow {
            color: #9a5b00; font-size: .76rem; font-weight: 750;
            letter-spacing: .12em; margin-bottom: -.4rem;
            text-transform: uppercase;
        }
        .review-subtitle {
            color: #526078; font-size: 1.05rem; line-height: 1.65;
            margin: -.45rem 0 1.3rem; max-width: 720px;
        }
        .review-guidance {
            background: #fffaf0; border: 1px solid #f0d9ae;
            border-radius: 12px; color: #67430c;
            margin-bottom: 1.25rem; padding: .8rem 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

apply_workspace_theme()

st.markdown(
    '<p class="review-eyebrow">Human-in-the-loop decision queue</p>',
    unsafe_allow_html=True,
)
st.title("Human Review")
st.markdown(
    """
    <p class="review-subtitle">
        Inspect answers that did not meet automatic approval rules and make
        the final publication decision with the original evidence in view.
    </p>
    <div class="review-guidance">
        Approve only when the answer is supported by the reference, directly
        addresses the question, and handles uncertainty responsibly.
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    review_runs = get_evaluation_runs(
        DATABASE_PATH,
        RunState.HUMAN_REVIEW,
    )
    evaluations = get_evaluations(DATABASE_PATH)
except Exception:
    st.error("The human-review queue could not be loaded.")
    review_runs = []
    evaluations = []

evaluation_by_id = {
    evaluation["evaluation_id"]: evaluation
    for evaluation in evaluations
}

st.metric("Awaiting human review", len(review_runs))

if not review_runs:
    st.info("No evaluation runs currently require human review.")

for run in review_runs:
    evaluation = evaluation_by_id.get(run["evaluation_id"])
    heading = f'Run {run["run_id"][:8]}'
    if evaluation:
        heading += f' · Score {evaluation["overall_score"]}/100'

    with st.expander(heading, expanded=True):
        st.write(f'**Question:** {run["question"]}')
        reference_column, answer_column = st.columns(2)
        with reference_column:
            st.subheader("Trusted reference")
            st.write(run["reference"])
        with answer_column:
            st.subheader("AI answer")
            st.write(run["answer"])

        if evaluation:
            score_column, concern_column = st.columns([1, 3])
            score_column.metric(
                "Overall score",
                f'{evaluation["overall_score"]}/100',
            )
            with concern_column:
                st.warning(
                    f'**Main concern:** {evaluation["main_concern"]}'
                )
                st.write(
                    "**System recommendation:** "
                    f'{evaluation["recommended_action"]}'
                )

            st.subheader("Quality scores")
            for dimension in evaluation["dimension_scores"]:
                st.write(
                    f'**{dimension["name"]}: '
                    f'{dimension["score"]}/100**'
                )
                st.caption(dimension["explanation"])
                for concern in dimension["concerns"]:
                    st.warning(concern)
        else:
            st.warning(
                "The linked evaluation could not be found. Review the "
                "submitted content carefully before deciding."
            )

        st.divider()
        st.write("**Final human decision**")
        approve_column, reject_column = st.columns(2)

        if approve_column.button(
            "Approve",
            key=f'approve-{run["run_id"]}',
            type="primary",
            use_container_width=True,
        ):
            try:
                resolve_human_review(
                    run["run_id"],
                    ReviewDecision.APPROVE,
                    DATABASE_PATH,
                )
                st.success("The run was approved.")
                st.rerun()
            except Exception:
                st.error("The review decision could not be saved.")

        if reject_column.button(
            "Reject",
            key=f'reject-{run["run_id"]}',
            use_container_width=True,
        ):
            try:
                resolve_human_review(
                    run["run_id"],
                    ReviewDecision.REJECT,
                    DATABASE_PATH,
                )
                st.success("The run was rejected.")
                st.rerun()
            except Exception:
                st.error("The review decision could not be saved.")
