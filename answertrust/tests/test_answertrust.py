from pathlib import Path
import pytest
import streamlit as st
from src.academic import extract_claims,match_evidence,split_sections
from src.database import get_evaluation_run
from src.evaluator import evaluate_answer
from src.example_data import load_examples,validate_examples
from src.experiments import run_experiment,run_matcher_comparison
from src.models import ClaimLabel,Decision,EvaluationInput,RunState
from src.nli import NLIClassifier,NLIPrediction,apply_nli
from src.review import ReviewDecision,resolve_human_review
from src.semantic import SemanticMatcher,cosine_similarity
from src.workflow import execute_evaluation_run

PAPER="METHODS\nAdults were randomly assigned.\nRESULTS\nTreatment improved outcomes in some participants.\nLIMITATIONS\nChildren were not studied."

def test_sections_and_claims():
    assert set(split_sections(PAPER))=={"METHODS","RESULTS","LIMITATIONS"}
    assert len(extract_claims("Treatment helped; however children were not studied."))==2

def test_overstatement_routes_to_review():
    result=evaluate_answer(EvaluationInput("Did treatment improve outcomes?",PAPER,"Treatment improved outcomes for all participants."))
    assert result.claim_results[0].label==ClaimLabel.PARTIALLY_SUPPORTED
    assert "OVERSTATED_CONCLUSION" in result.claim_results[0].failure_types
    assert result.final_decision==Decision.REVIEW
    assert result.claim_results[0].evidence[0].section=="RESULTS"

def test_contradiction_rejected():
    result=evaluate_answer(EvaluationInput("Did treatment improve sleep?","RESULTS\nTreatment did not improve sleep.","Treatment improved sleep."))
    assert result.claim_results[0].label==ClaimLabel.CONTRADICTED
    assert result.final_decision==Decision.REJECT

def test_retry_and_review_audit(tmp_path:Path):
    calls={"count":0}
    def flaky(item,**kwargs):
        calls["count"]+=1
        if calls["count"]==1: raise TimeoutError("temporary")
        return evaluate_answer(item)
    run_id,_=execute_evaluation_run(EvaluationInput("Did treatment improve outcomes?",PAPER,"Treatment improved outcomes for all participants."),tmp_path/"db.sqlite",evaluator=flaky)
    run=get_evaluation_run(run_id,tmp_path/"db.sqlite")
    assert run["attempt_count"]==2 and run["state"]==RunState.HUMAN_REVIEW.value
    resolve_human_review(run_id,ReviewDecision.REJECT,tmp_path/"db.sqlite","Universal wording is not supported.")
    run=get_evaluation_run(run_id,tmp_path/"db.sqlite")
    assert run["system_decision"]=="REVIEW" and run["reviewer_decision"]=="REJECT"
    assert run["reviewer_notes"]=="Universal wording is not supported."

def test_benchmark_schema_and_metrics():
    examples=load_examples(); assert len(examples)==50; assert validate_examples(examples)==[]
    rows,metrics=run_experiment(write_output=False)
    assert len(rows)==50
    assert {"unsupported_detection_rate_pct","contradiction_detection_rate_pct","false_publish_rate_pct","review_rate_pct"} <= set(metrics)


class FakeEncoder:
    """Map a known paraphrase and evidence sentence to nearby vectors."""
    def encode(self, sentences, **kwargs):
        vectors={
            "The intervention made participants rest better.":[1.0,0.0],
            "Therapy improved sleep quality.":[0.98,0.02],
            "Participants reported their weekly diet.":[0.0,1.0],
            "The intervention was described to participants.":[0.2,0.8],
        }
        return [vectors[sentence] for sentence in sentences]


def test_semantic_matcher_finds_paraphrased_evidence():
    matcher=SemanticMatcher(encoder=FakeEncoder())
    result=evaluate_answer(
        EvaluationInput(
            "Did the intervention improve rest?",
            "METHODS\nParticipants reported their weekly diet.\nRESULTS\nTherapy improved sleep quality.",
            "The intervention made participants rest better.",
        ),
        semantic_matcher=matcher,
    )
    assert result.claim_results[0].evidence[0].section=="RESULTS"
    assert result.claim_results[0].label==ClaimLabel.SUPPORTED


def test_semantic_failure_falls_back_to_lexical_matching():
    class BrokenMatcher:
        def similarities(self, claim, passages): raise RuntimeError("model unavailable")
    result=evaluate_answer(
        EvaluationInput("Did treatment improve sleep?","RESULTS\nTreatment improved sleep.","Treatment improved sleep."),
        semantic_matcher=BrokenMatcher(),
    )
    assert result.claim_results[0].label==ClaimLabel.SUPPORTED


def test_semantic_meaning_outranks_shallow_keyword_overlap():
    matcher=SemanticMatcher(encoder=FakeEncoder())
    sections=split_sections(
        "METHODS\nThe intervention was described to participants.\n"
        "RESULTS\nTherapy improved sleep quality."
    )
    evidence=match_evidence(
        "The intervention made participants rest better.",
        sections,
        limit=1,
        semantic_matcher=matcher,
    )
    assert evidence[0].section=="RESULTS"


def test_results_prior_breaks_close_semantic_tie():
    class CloseEncoder:
        def encode(self, sentences, **kwargs):
            return [[1.0,0.0],[0.9,0.1],[0.88,0.12]]
    evidence=match_evidence(
        "The intervention improved outcomes.",
        {"METHODS":"The intervention was administered.","RESULTS":"Outcomes became better."},
        limit=1,
        semantic_matcher=SemanticMatcher(encoder=CloseEncoder()),
    )
    assert evidence[0].section=="RESULTS"


class FakeNLIModel:
    def __init__(self, scores): self.scores=scores
    def predict(self, pairs): return [self.scores]


def test_nli_predicts_entailment_and_confidence():
    prediction=NLIClassifier(model=FakeNLIModel([0.0,4.0,0.0])).predict(
        "Therapy improved sleep.","Treatment helped participants rest."
    )
    assert prediction.label=="entailment"
    assert prediction.confidence>0.9


def test_confident_nli_contradiction_overrides_heuristic():
    result=evaluate_answer(
        EvaluationInput("Did treatment improve sleep?","RESULTS\nTreatment improved sleep.","Treatment improved sleep."),
        nli_classifier=NLIClassifier(model=FakeNLIModel([5.0,0.0,0.0])),
    )
    assert result.claim_results[0].label==ClaimLabel.CONTRADICTED
    assert result.final_decision==Decision.REJECT


def test_low_confidence_nli_does_not_override():
    base=evaluate_answer(EvaluationInput("Did treatment improve sleep?","RESULTS\nTreatment improved sleep.","Treatment improved sleep."))
    claim=base.claim_results[0]
    apply_nli(claim,NLIPrediction("contradiction",0.4))
    assert claim.label==ClaimLabel.SUPPORTED


def test_nli_failure_falls_back_to_heuristic():
    class BrokenNLI:
        def predict(self,evidence,claim): raise RuntimeError("unavailable")
    result=evaluate_answer(
        EvaluationInput("Did treatment improve sleep?","RESULTS\nTreatment improved sleep.","Treatment improved sleep."),
        nli_classifier=BrokenNLI(),
    )
    assert result.claim_results[0].label==ClaimLabel.SUPPORTED


def test_participants_does_not_trigger_patients_scope_flag():
    result=evaluate_answer(
        EvaluationInput(
            "Did treatment improve sleep?",
            "RESULTS\nTreatment did not improve sleep.",
            "Treatment improved sleep.",
        )
    )
    assert "OUTSIDE_STUDIED_SCOPE" not in result.claim_results[0].failure_types


def test_cosine_similarity_handles_zero_vector():
    assert cosine_similarity([0.0,0.0],[1.0,1.0])==0.0


def test_required_streamlit_navigation_api_is_available():
    assert callable(st.switch_page)


def test_matcher_comparison_reports_before_and_after(tmp_path):
    examples=tmp_path/"semantic.json"
    examples.write_text(
        '[{"id":"one","claim":"The intervention made participants rest better.",'
        '"paper_text":"METHODS\\nParticipants reported their weekly diet.\\nRESULTS\\nTherapy improved sleep quality.",'
        '"expected_section":"RESULTS","expected_passage":"Therapy improved sleep quality."}]',
        encoding="utf-8",
    )
    _,metrics=run_matcher_comparison(
        SemanticMatcher(encoder=FakeEncoder()), examples
    )
    assert metrics["lexical_top_passage_accuracy_pct"]==0.0
    assert metrics["semantic_top_passage_accuracy_pct"]==100.0
    assert metrics["absolute_improvement_points"]==100.0
