"""Measured benchmark dashboard connected to the AnswerTrust API."""

import streamlit as st

from src.api_client import AnswerTrustAPIClient
from src.experiments import run_matcher_comparison, run_nli_benchmark
from src.ui import apply_theme, hero

st.set_page_config(page_title="Benchmarks | AnswerTrust", page_icon="A", layout="wide")
apply_theme()
hero("Measured, not assumed", "Evaluation benchmarks.", "Inspect the labelled regression sets used to measure publication safety, semantic retrieval, and natural-language inference.", tone="sky")

api = AnswerTrustAPIClient()
st.subheader("Publication safety")
st.caption("50 self-authored paper-grounded examples / deterministic baseline")

if st.button("Run publication benchmark", type="primary"):
    try:
        with st.spinner("Running and saving the publication benchmark..."):
            st.session_state["publication_benchmark"] = api.run_publication_benchmark()
    except Exception:
        st.error("The benchmark API is unavailable. Start FastAPI and try again.")

benchmark = st.session_state.get("publication_benchmark")
if benchmark:
    safety = benchmark["metrics"]
    columns = st.columns(5)
    items = [
        ("Examples", "total_examples"),
        ("Decision accuracy", "decision_accuracy_pct"),
        ("Unsupported detection", "unsupported_detection_rate_pct"),
        ("Contradiction detection", "contradiction_detection_rate_pct"),
        ("False-publish rate", "false_publish_rate_pct"),
    ]
    for column, (label, key) in zip(columns, items):
        value = safety[key]
        column.metric(label, value if key == "total_examples" else f"{value}%")
    with st.expander("Publication benchmark examples"):
        st.dataframe(
            [result["details"] for result in benchmark["results"]],
            use_container_width=True,
        )

try:
    saved_runs = api.list_benchmarks()
except Exception:
    saved_runs = []
if saved_runs:
    with st.expander("Saved benchmark runs"):
        st.dataframe(
            [
                {
                    "run_id": run["run_id"],
                    "name": run["benchmark_name"],
                    "status": run["status"],
                    "started_at": run["started_at"],
                    **(run["metrics"] or {}),
                }
                for run in saved_runs
            ],
            use_container_width=True,
        )

st.markdown("---")
st.subheader("ML evaluations")
st.caption("Models run locally and may take several seconds on first use.")
if st.button("Run ML benchmarks"):
    with st.spinner("Running semantic retrieval and NLI benchmarks..."):
        _, retrieval = run_matcher_comparison()
        nli_rows, nli = run_nli_benchmark()
    retrieval_columns = st.columns(3)
    retrieval_columns[0].metric("Keyword retrieval", f'{retrieval["lexical_top_passage_accuracy_pct"]}%')
    retrieval_columns[1].metric("Semantic retrieval", f'{retrieval["semantic_top_passage_accuracy_pct"]}%')
    retrieval_columns[2].metric("Absolute improvement", f'+{retrieval["absolute_improvement_points"]} pts')
    st.markdown("#### Natural-language inference")
    nli_columns = st.columns(5)
    nli_items = [
        ("Accuracy", "accuracy_pct"),
        ("Coverage", "coverage_pct"),
        ("Entailment recall", "entailment_recall_pct"),
        ("Contradiction recall", "contradiction_recall_pct"),
        ("Neutral recall", "neutral_recall_pct"),
    ]
    for column, (label, key) in zip(nli_columns, nli_items):
        column.metric(label, f'{nli[key]}%')
    st.info(f'False entailment: {nli["false_entailment_rate_pct"]}% · False contradiction: {nli["false_contradiction_rate_pct"]}% · Abstention: {nli["abstention_rate_pct"]}%')
    with st.expander("NLI example predictions"):
        st.dataframe(nli_rows, use_container_width=True)

st.caption("Small, deliberately constructed project benchmarks—not estimates of general performance on academic literature.")
