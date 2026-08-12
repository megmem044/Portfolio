"""Measured benchmark dashboard."""
import streamlit as st
from src.experiments import run_experiment

st.set_page_config(page_title="Benchmark | AnswerTrust",layout="wide")
st.title("Academic benchmark")
rows,metrics=run_experiment(write_output=False)
cols=st.columns(5)
for column,(label,key) in zip(cols,[("Examples","total_examples"),("Decision accuracy","decision_accuracy_pct"),("Unsupported detection","unsupported_detection_rate_pct"),("Contradiction detection","contradiction_detection_rate_pct"),("False-publish rate","false_publish_rate_pct")]):
    value=metrics[key]; column.metric(label,value if key=="total_examples" else f"{value}%")
st.metric("Human-review rate",f'{metrics["review_rate_pct"]}%')
st.dataframe(rows,use_container_width=True)
