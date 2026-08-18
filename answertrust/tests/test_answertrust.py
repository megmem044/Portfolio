from pathlib import Path
from src.academic import extract_claims,match_evidence,split_sections
from src.evaluator import evaluate_answer
from src.example_data import load_examples,validate_examples
from src.experiments import calculate_nli_metrics,export_disagreements,nli_threshold_sweep,run_experiment,run_matcher_comparison,run_nli_benchmark
from src.models import ClaimLabel,Decision,EvaluationInput
from src.nli import LABELS,NLIClassifier,NLIPrediction,apply_nli
from src.retrieval import AcademicEvidenceRetriever
from src.semantic import SemanticMatcher,cosine_similarity
from src.config import MODEL_CACHE_DIR,configure_model_cache
from src.classification import AcademicClaimClassifier
from src.pipeline import EvaluationPipeline

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

def test_small_percentage_contradicts_most_claim():
    result=evaluate_answer(EvaluationInput("Were most associations strong?","RESULTS\nOnly 5% of statistically significant associations were strong.","Most statistically significant associations were strong."))
    assert result.claim_results[0].label==ClaimLabel.CONTRADICTED
    assert result.final_decision==Decision.REJECT

def test_reversed_numeric_comparison_is_rejected():
    result=evaluate_answer(EvaluationInput("Which effect was larger?","RESULTS\nSummed effects were 6279; total treatment effect was 5455.","The total treatment effect was larger than the summed effects."))
    assert result.claim_results[0].label==ClaimLabel.CONTRADICTED
    assert result.final_decision==Decision.REJECT

def test_nonsignificant_result_contradicts_significant_claim():
    result=evaluate_answer(EvaluationInput("Was the difference significant?","RESULTS\nThe difference was not significant (p = 0.42).","The difference was statistically significant."))
    assert result.claim_results[0].label==ClaimLabel.CONTRADICTED
    assert result.final_decision==Decision.REJECT

def test_low_relevance_alone_does_not_reject_supported_claim():
    result=evaluate_answer(EvaluationInput("What safeguard was recommended?","CONCLUSION\nPotential publication bias should be investigated when assessing placebo-effect magnitude.","Assessments of placebo-effect magnitude should investigate publication bias."))
    assert result.claim_results[0].label==ClaimLabel.SUPPORTED
    assert result.final_decision==Decision.PUBLISH

def test_unrelated_opposites_do_not_create_a_contradiction():
    result=evaluate_answer(EvaluationInput("Did tutoring reduce anxiety?","RESULTS\nAttendance at tutoring was high.","Tutoring reduced anxiety."))
    assert result.claim_results[0].label==ClaimLabel.UNSUPPORTED
    assert result.final_decision==Decision.REJECT

def test_non_positive_matches_not_positive():
    result=evaluate_answer(EvaluationInput("How was spin defined?","METHODS\nSpin describes results as beneficial even though they were not positive.","Spin presents non-positive results as beneficial."))
    assert result.claim_results[0].label!=ClaimLabel.CONTRADICTED

def test_inclusive_table_range_supports_enumerated_tables():
    result=evaluate_answer(EvaluationInput("Where were results summarized?","RESULTS\nResults were summarized in Tables 2 through 4.","Results were summarized in Tables 2, 3, and 4."))
    assert result.claim_results[0].label==ClaimLabel.SUPPORTED
    assert result.final_decision==Decision.PUBLISH

def test_lack_matches_did_not_include():
    result=evaluate_answer(EvaluationInput("What problem was identified?","EDITORIAL ASSESSMENT\nThe analysis did not include a robust statistical analysis.","Editors identified a lack of robust statistical analysis."))
    assert result.claim_results[0].label!=ClaimLabel.CONTRADICTED

def test_valid_p_value_threshold_is_supported():
    result=evaluate_answer(EvaluationInput("Was the difference significant?","RESULTS\nThe reported difference had p = 0.049.","The difference met the p < 0.05 threshold."))
    assert result.claim_results[0].label==ClaimLabel.SUPPORTED
    assert result.final_decision==Decision.PUBLISH

def test_faithful_limitation_does_not_require_extra_qualification():
    result=evaluate_answer(EvaluationInput("Why was simulation used?","LIMITATIONS\nSimulation allowed control over the underlying distribution.","Simulation was used to control the underlying distribution."))
    assert "MISSING_QUALIFICATION" not in result.claim_results[0].failure_types

def test_benchmark_schema_and_metrics():
    examples=load_examples(); assert len(examples)==150; assert validate_examples(examples)==[]
    assert {item["schema_version"] for item in examples}=={2}
    assert {item["source_type"] for item in examples}=={"SYNTHETIC","REAL_EXCERPT"}
    assert sum(item["source_type"]=="REAL_EXCERPT" for item in examples)==100
    assert all(item["label_rationale"] for item in examples)
    rows,metrics=run_experiment(write_output=False)
    assert len(rows)==150
    assert {"unsupported_detection_rate_pct","contradiction_detection_rate_pct","false_publish_rate_pct","review_rate_pct"} <= set(metrics)
    assert {"source_type","difficulty_category","reviewer_confidence"} <= set(rows[0])

def test_disagreement_export_is_deidentified(tmp_path):
    rows=[{"id":"case-1","category":"numerical","source_type":"REAL_EXCERPT","source_locator":"https://doi.org/example","difficulty_category":"HARD","annotation_status":"PROJECT_AUTHORED","reviewer_label":"SUPPORTED","reviewer_confidence":0.9,"actual_claim_label":"CONTRADICTED","expected_decision":"PUBLISH","actual_decision":"REJECT","question":"private","paper_text":"private","answer":"private"}]
    exported=export_disagreements(rows,tmp_path/"disagreements.csv")
    content=(tmp_path/"disagreements.csv").read_text(encoding="utf-8")
    assert len(exported)==1
    assert "private" not in content


def test_real_benchmark_excerpt_requires_provenance():
    examples=load_examples()
    examples[0]={**examples[0],"source_type":"REAL_EXCERPT","source_title":"Open paper","source_locator":"","reuse_license":"CC-BY-4.0","excerpt_section":"RESULTS"}
    assert "Example 1 real excerpt requires source_locator." in validate_examples(examples)


def test_benchmark_reviewer_confidence_is_bounded():
    examples=load_examples();examples[0]={**examples[0],"reviewer_confidence":1.2}
    assert "Example 1 reviewer confidence must be between 0 and 1." in validate_examples(examples)


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


def test_evaluator_uses_evidence_retriever_interface():
    class FixedRetriever:
        def retrieve(self, claim, sections, limit=2):
            return AcademicEvidenceRetriever().retrieve(claim, sections, limit)

    result=evaluate_answer(
        EvaluationInput(
            "Did treatment improve sleep?",
            "RESULTS\nTreatment improved sleep.",
            "Treatment improved sleep.",
        ),
        evidence_retriever=FixedRetriever(),
    )
    assert result.claim_results[0].label==ClaimLabel.SUPPORTED


def test_pipeline_connects_retrieval_and_classification():
    pipeline=EvaluationPipeline(AcademicEvidenceRetriever(),AcademicClaimClassifier())
    result=pipeline.evaluate(
        EvaluationInput(
            "Did treatment improve sleep?",
            "RESULTS\nTreatment improved sleep.",
            "Treatment improved sleep.",
        )
    )
    assert result.final_decision==Decision.PUBLISH


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


def test_nli_only_contradiction_routes_to_review():
    result=evaluate_answer(
        EvaluationInput("Did treatment improve sleep?","RESULTS\nTreatment improved sleep.","Treatment improved sleep."),
        nli_classifier=NLIClassifier(model=FakeNLIModel([5.0,0.0,0.0])),
    )
    assert result.claim_results[0].label==ClaimLabel.CONTRADICTED
    assert "NLI_ONLY_CONTRADICTION" in result.claim_results[0].failure_types
    assert result.final_decision==Decision.REVIEW


def test_confirmed_contradiction_still_rejects_with_nli():
    result=evaluate_answer(
        EvaluationInput("Did treatment improve sleep?","RESULTS\nTreatment did not improve sleep.","Treatment improved sleep."),
        nli_classifier=NLIClassifier(model=FakeNLIModel([5.0,0.0,0.0])),
    )
    assert "NLI_ONLY_CONTRADICTION" not in result.claim_results[0].failure_types
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


def test_nli_metrics_report_recall_coverage_and_abstention():
    rows=[
        {"expected_label":"entailment","actual_label":"entailment","confidence":0.9},
        {"expected_label":"contradiction","actual_label":"contradiction","confidence":0.8},
        {"expected_label":"neutral","actual_label":"entailment","confidence":0.5},
    ]
    metrics=calculate_nli_metrics(rows)
    assert metrics["accuracy_pct"]==66.67
    assert metrics["coverage_pct"]==66.67
    assert metrics["covered_accuracy_pct"]==100.0
    assert metrics["neutral_recall_pct"]==0.0
    assert metrics["false_entailment_rate_pct"]==50.0
    assert metrics["false_contradiction_rate_pct"]==0.0


def test_nli_threshold_sweep_trades_coverage_for_abstention():
    rows=[
        {"expected_label":"entailment","actual_label":"entailment","confidence":0.96},
        {"expected_label":"neutral","actual_label":"neutral","confidence":0.6},
    ]
    sweep=nli_threshold_sweep(rows)
    assert sweep[0]["coverage_pct"]==100.0
    assert sweep[-1]["coverage_pct"]==50.0
    assert sweep[-1]["abstention_rate_pct"]==50.0


def test_nli_benchmark_loads_balanced_dataset():
    class ExpectedClassifier:
        def predict(self,evidence,claim):
            if "not " in evidence or any(word in evidence for word in ("increased reported pain","equal infection","did not change","raised systolic","reduced clinic attendance","worse mood","fewer words","increased symptoms","not associated")):
                return NLIPrediction("contradiction",0.9)
            if any(phrase in claim for phrase in ("blood pressure","employment","mathematical ability","asthma incidence","influenza","pain severity","household income","air pollution","school attendance","memory recall")) and not any(term in evidence for term in claim.split()[-2:]):
                return NLIPrediction("neutral",0.9)
            return NLIPrediction("entailment",0.9)
    rows,metrics=run_nli_benchmark(classifier=ExpectedClassifier())
    assert len(rows)==30
    assert {row["expected_label"] for row in rows}==set(LABELS)
    assert "abstention_rate_pct" in metrics


def test_model_cache_environment_is_project_local(monkeypatch):
    monkeypatch.delenv("HF_HOME",raising=False)
    configure_model_cache()
    import os
    assert os.environ["HF_HOME"]==str(MODEL_CACHE_DIR)


def test_cosine_similarity_handles_zero_vector():
    assert cosine_similarity([0.0,0.0],[1.0,1.0])==0.0


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
