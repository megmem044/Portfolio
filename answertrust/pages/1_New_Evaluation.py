"""Streamlit entry point for AnswerTrust."""

import streamlit as st

from src.config import DATABASE_PATH
from src.models import Decision, EvaluationInput, EvaluationResult
from src.transformer_evaluator import (
    LocalTransformerEvaluator,
    PROMPT_VERSIONS,
)
from src.ui import apply_workspace_theme
from src.workflow import execute_evaluation_run


st.set_page_config(
    page_title="AnswerTrust",
    page_icon="âœ…",
    layout="wide",
)


st.markdown(
    """
    <style>
        :root {
            --arcade-bg: #fff7e8;
            --arcade-panel: #ffffff;
            --arcade-blue: #2b193d;
            --arcade-pink: #ff6b5e;
            --arcade-yellow: #c7f464;
            --arcade-mint: #2ec4b6;
            --arcade-text: #2b193d;
            --at-lilac: #b8a1ff;
        }
        .stApp {
            background-color: var(--arcade-bg);
            background-image:
                linear-gradient(rgba(43,25,61,.045) 1px, transparent 1px),
                linear-gradient(90deg, rgba(43,25,61,.045) 1px, transparent 1px);
            background-size: 44px 44px;
        }
        [data-testid="stHeader"] { background: rgba(255,247,232,.94); }
        [data-testid="stHeader"]::before {
            background: linear-gradient(90deg, var(--arcade-blue) 0 34%,
                        var(--arcade-pink) 34% 67%, var(--arcade-yellow) 67%);
            content: ""; height: 4px; left: 0; position: fixed;
            right: 0; top: 0; z-index: 999;
        }
        [data-testid="stSidebar"] {
            background: #2b193d;
            border-right: 4px solid var(--at-lilac);
        }
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarNav"] {
            background-color: #2b193d !important;
            background-image: none !important;
            box-shadow: none !important;
        }
        [data-testid="stSidebarNav"]::before,
        [data-testid="stSidebarNav"]::after {
            background: none !important;
            box-shadow: none !important;
            display: none !important;
        }
        [data-testid="stSidebar"] * {
            -webkit-mask-image: none !important;
            background-image: none !important;
            box-shadow: none !important;
            filter: none !important;
            mask-image: none !important;
            text-shadow: none !important;
        }
        [data-testid="stSidebar"] *::before,
        [data-testid="stSidebar"] *::after {
            -webkit-mask-image: none !important;
            background: transparent !important;
            background-image: none !important;
            box-shadow: none !important;
            filter: none !important;
            mask-image: none !important;
        }
        [data-testid="stSidebar"] * { color: #f8fafc; }
        [data-testid="stSidebarNav"] a:hover {
            background: rgba(255,255,255,.1);
        }
        .block-container { max-width: 1120px; padding-top: 1.75rem; }
        h1, h2, h3 { color: var(--arcade-text); letter-spacing: -.018em; }
        .main p, .main label { color: #51445b; }
        div[data-testid="stForm"] {
            background: rgba(255,255,255,.97);
            border: 2px solid var(--arcade-blue);
            border-top: 7px solid var(--arcade-pink);
            border-radius: 16px;
            box-shadow: 8px 8px 0 var(--arcade-yellow);
            padding: 1.2rem 1.25rem 1.25rem;
        }
        div[data-testid="stForm"]:hover {
            box-shadow: 8px 8px 0 var(--arcade-yellow);
        }
        div[data-testid="stTextArea"] textarea {
            background: #fffbf4; border-color: #d9ccdc; border-radius: 9px;
            color: #2b193d;
        }
        div[data-testid="stTextArea"] textarea:focus {
            border-color: var(--arcade-blue);
            box-shadow: 0 0 0 1px var(--arcade-blue);
        }
        div[data-testid="stMetric"] {
            background: var(--arcade-panel); border: 1px solid var(--arcade-blue);
            border-radius: 8px; padding: .8rem .9rem;
        }
        div[data-testid="stAlert"] { border-radius: 8px; }
        div[data-testid="stFormSubmitButton"] button {
            background-image: linear-gradient(110deg, transparent 25%,
                              rgba(255,255,255,.45) 45%, transparent 65%);
            background-position: 140% 0; background-repeat: no-repeat;
            background-size: 60% 100%;
            background-color: var(--arcade-yellow);
            border: 2px solid var(--arcade-yellow);
            border-radius: 999px; color: #2b193d; font-weight: 800;
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            background: var(--arcade-pink); border-color: var(--arcade-pink);
            color: #fff;
        }
        .app-breadcrumb {
            color: #7b647f; font-size: .78rem; font-weight: 750;
            letter-spacing: .1em; margin-bottom: .45rem; text-transform: uppercase;
        }
        .app-heading-row {
            align-items: center; display: flex; justify-content: space-between;
            margin-bottom: .25rem;
        }
        .app-heading-row h1 {
            font-size: 2rem; margin: 0; padding: 0;
        }
        .app-status {
            background: #ddf8ef; border: 1px solid var(--arcade-mint);
            border-radius: 999px; color: #14796f; font-size: .72rem;
            font-weight: 750; letter-spacing: .08em; padding: .28rem .7rem;
        }
        .app-description {
            color: #6f6174; font-size: .96rem; margin: .2rem 0 .9rem;
        }
        .section-label {
            color: var(--arcade-yellow); font-size: .8rem; font-weight: 800;
            letter-spacing: .08em; text-transform: uppercase;
            margin-bottom: .2rem;
        }
        .app-tools {
            align-items: center; display: flex; flex-wrap: wrap;
            gap: .5rem; margin-bottom: 1.35rem;
        }
        .app-chip {
            background: #fff; border: 1px solid #ddcfdf;
            border-radius: 999px; color: #54435b; font-size: .73rem;
            font-weight: 650;
            padding: .35rem .65rem;
        }
        .app-chip::before {
            background: var(--arcade-yellow); border-radius: 50%; content: "";
            display: inline-block; height: 6px; margin-right: .45rem; width: 6px;
        }
        hr { border-color: #e3e6eb; }
        @media (max-width: 700px) {
            .app-heading-row { align-items: flex-start; flex-direction: column; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

apply_workspace_theme()


st.markdown(
    """
    <style>
        :root { --ink:#2c2c34; --coral:#ff7d59; --pink:#ffbde8;
            --periwinkle:#9980ed; --sky:#cddbf9; --paper:#fffdf8;
            --muted:#62616e; }
        .stApp { background:var(--sky)!important; background-image:none!important; }
        [data-testid="stHeader"] { background:rgba(205,219,249,.94)!important; }
        [data-testid="stHeader"]::before { background:var(--coral)!important; }
        [data-testid="stSidebar"] { background:var(--ink)!important;
            border-right:0!important; }
        [data-testid="stSidebar"] > div, [data-testid="stSidebarNav"] {
            background:var(--ink)!important; }
        [data-testid="stSidebarNav"]::before {
            background:transparent!important; color:var(--paper)!important;
            content:"AnswerTrust"!important; display:block!important;
            font-family:Georgia,"Times New Roman",serif!important;
            font-size:2rem!important; font-weight:700!important;
            letter-spacing:-.04em!important; line-height:1!important;
            padding:2.1rem 1.5rem .55rem!important;
        }
        [data-testid="stSidebarNav"] ul {
            margin-top:0!important; padding-top:0!important;
        }
        [data-testid="stSidebar"] * { color:var(--paper)!important; }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background:var(--coral)!important; }
        [data-testid="stSidebarNav"] a:hover { background:#44434d!important; }
        .block-container { max-width:1120px; padding-top:2.25rem; }
        h1,h2,h3 { color:var(--ink)!important; }
        .app-heading-row h1 { font-family:Georgia,"Times New Roman",serif;
            font-size:2.2rem; letter-spacing:-.04em; }
        .app-breadcrumb { color:var(--periwinkle); }
        .app-description { color:var(--muted); margin-bottom:1.35rem; }
        .app-status { background:var(--paper); border:1px solid var(--ink);
            color:var(--ink); letter-spacing:.06em; }
        div[data-testid="stForm"] { background:var(--paper);
            border:2px solid var(--ink); border-top:2px solid var(--ink);
            border-radius:20px; box-shadow:10px 10px 0 var(--periwinkle);
            padding:1.45rem 1.5rem 1.5rem; }
        div[data-testid="stForm"]:hover { box-shadow:10px 10px 0 var(--periwinkle); }
        .section-label { color:var(--coral); }
        div[data-testid="stTextArea"] textarea { background:#fff;
            border:1px solid #cac8d2; color:var(--ink); }
        div[data-testid="stTextArea"] textarea:focus { border-color:var(--periwinkle);
            box-shadow:0 0 0 1px var(--periwinkle); }
        div[data-testid="stFormSubmitButton"] button { background:var(--coral);
            border:2px solid var(--coral); border-radius:12px; color:#fff; }
        div[data-testid="stFormSubmitButton"] button:hover {
            background:var(--periwinkle); border-color:var(--periwinkle); }
        div[data-testid="stExpander"] { background:#fff; border-color:#cac8d2;
            border-radius:10px; }
        div[data-testid="stMetric"] { background:var(--paper);
            border:2px solid var(--ink); border-radius:14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_transformer_evaluator() -> LocalTransformerEvaluator:
    """Create one lazy local-model wrapper per Streamlit process."""
    return LocalTransformerEvaluator()


def show_decision(decision: Decision) -> None:
    """Display the publication decision prominently."""

    messages = {
        Decision.PUBLISH: "PUBLISH â€” This answer meets the current quality rules.",
        Decision.REVIEW: "REVIEW â€” Check the concerns before publishing.",
        Decision.REJECT: "REJECT â€” This answer requires substantial revision.",
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
            f"Prompt: {result.prompt_version} Â· "
            f"Transformer latency: {result.transformer_latency_ms} ms"
        )
    elif result.model_status != "not_used":
        st.info(
            "The optional local transformer was unavailable or returned an "
            "invalid response. The deterministic result above remains valid."
        )


with st.sidebar:
    st.title("AnswerTrust")
    st.write("Evaluation operations")

st.markdown(
    """
    <div class="app-breadcrumb">Evaluations</div>
    <div class="app-heading-row">
        <h1>New evaluation</h1>
        <span class="app-status">â— READY</span>
    </div>
    <p class="app-description">
        Check an answer against a trusted reference.
    </p>
    <div class="app-tools">
        <span class="app-chip">5 quality checks</span>
        <span class="app-chip">Local history</span>
        <span class="app-chip">Human review routing</span>
    </div>
    """,
    unsafe_allow_html=True,
)
with st.form("evaluation_form"):
    st.markdown(
        '<div class="section-label">What do you want to verify?</div>',
        unsafe_allow_html=True,
    )
    question = st.text_area(
        "Verification question",
        placeholder="Example: Does this response correctly explain the refund policy?",
        height=120,
        help="State the specific question the information should answer.",
    )

    reference_column, answer_column = st.columns(2)
    with reference_column:
        reference = st.text_area(
            "Trusted reference",
            placeholder="Paste the policy, document excerpt, notes, or other source you trust.",
            height=230,
            help="AnswerTrust treats this as the evidence for the check.",
        )
    with answer_column:
        answer = st.text_area(
            "Information to verify",
            placeholder="Paste the claim, response, summary, or generated text you want to check.",
            height=230,
            help="This text will be compared with the trusted reference.",
        )

    with st.expander("Advanced options"):
        use_transformer = st.checkbox(
            "Use optional local transformer explanation",
            help=(
                "Requires google/flan-t5-small in the local Hugging Face "
                "cache. The model never overrides the official decision."
            ),
        )
        prompt_version = st.selectbox(
            "Transformer prompt",
            options=PROMPT_VERSIONS,
            disabled=not use_transformer,
        )

    submitted = st.form_submit_button(
        "Verify information",
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
    try:
        run_id, evaluation_result = execute_evaluation_run(
            evaluation_input,
            DATABASE_PATH,
            transformer_evaluator=transformer_evaluator,
        )
    except Exception:
        st.error(
            "The evaluation run failed. Its FAILED state was saved for "
            "later inspection."
        )
        st.stop()

    show_result(evaluation_result)

    is_valid_evaluation = (
        evaluation_result.dimension_scores[0].name != "Validation"
    )
    if is_valid_evaluation:
        st.caption("Evaluation saved to local history.")
