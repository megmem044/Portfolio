from pathlib import Path
import pytest
from src.academic import extract_claims,split_sections
from src.database import get_evaluation_run
from src.evaluator import evaluate_answer
from src.example_data import load_examples,validate_examples
from src.experiments import run_experiment
from src.models import ClaimLabel,Decision,EvaluationInput,RunState
from src.review import ReviewDecision,resolve_human_review
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
