"""Run the labelled safety and semantic-retrieval benchmarks."""
import argparse
import csv
import json
from pathlib import Path
from src.academic import match_evidence, split_sections
from src.config import DISAGREEMENT_RESULTS_PATH, EXPERIMENT_RESULTS_PATH, NLI_EXAMPLES_PATH, SEMANTIC_EXAMPLES_PATH
from src.evaluator import evaluate_answer
from src.example_data import load_examples,validate_examples
from src.models import EvaluationInput
from src.nli import LABELS, NLIClassifier
from src.semantic import SemanticMatcher

def calculate_metrics(rows:list[dict])->dict:
    total=len(rows); unsafe=[r for r in rows if r["expected_decision"]!="PUBLISH"]
    unsupported=[r for r in rows if r["expected_claim_label"]=="UNSUPPORTED"]
    contradicted=[r for r in rows if r["expected_claim_label"]=="CONTRADICTED"]
    pct=lambda n,d: round(100*n/d,2) if d else 0.0
    return {"total_examples":total,"decision_accuracy_pct":pct(sum(r["expected_decision"]==r["actual_decision"] for r in rows),total),"unsupported_detection_rate_pct":pct(sum(r["actual_claim_label"]=="UNSUPPORTED" for r in unsupported),len(unsupported)),"contradiction_detection_rate_pct":pct(sum(r["actual_claim_label"]=="CONTRADICTED" for r in contradicted),len(contradicted)),"false_publish_rate_pct":pct(sum(r["actual_decision"]=="PUBLISH" for r in unsafe),len(unsafe)),"review_rate_pct":pct(sum(r["actual_decision"]=="REVIEW" for r in rows),total)}

def export_disagreements(rows:list[dict],path:Path=DISAGREEMENT_RESULTS_PATH)->list[dict]:
    """Write de-identified rows where the system differs from the reviewer."""
    disagreements=[row for row in rows if row["reviewer_label"]!=row["actual_claim_label"] or row["expected_decision"]!=row["actual_decision"]]
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=["id","category","source_type","source_locator","difficulty_category","annotation_status","reviewer_label","reviewer_confidence","actual_claim_label","expected_decision","actual_decision"]
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields); writer.writeheader()
        writer.writerows({field:row[field] for field in fields} for row in disagreements)
    return disagreements

def run_experiment(path:Path=EXPERIMENT_RESULTS_PATH,write_output:bool=True):
    examples=load_examples(); errors=validate_examples(examples)
    if errors: raise ValueError("; ".join(errors))
    rows=[]
    for item in examples:
        result=evaluate_answer(EvaluationInput(item["question"],item["paper_text"],item["answer"]))
        rows.append({"id":item["id"],"category":item["category"],"source_type":item["source_type"],"source_locator":item["source_locator"],"difficulty_category":item["difficulty_category"],"annotation_status":item["annotation_status"],"reviewer_label":item["reviewer_label"],"reviewer_confidence":item["reviewer_confidence"],"expected_claim_label":item["expected_claim_label"],"actual_claim_label":result.claim_results[0].label.value,"expected_decision":item["expected_decision"],"actual_decision":result.final_decision.value})
    if write_output:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("w",newline="",encoding="utf-8") as handle:
            writer=csv.DictWriter(handle,fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
        export_disagreements(rows)
    return rows,calculate_metrics(rows)


def run_matcher_comparison(
    matcher: SemanticMatcher | None = None,
    examples_path: Path = SEMANTIC_EXAMPLES_PATH,
) -> tuple[list[dict], dict]:
    """Compare top-passage accuracy for lexical and semantic matching."""
    with examples_path.open(encoding="utf-8") as handle:
        examples = json.load(handle)
    matcher = matcher or SemanticMatcher()
    rows = []
    for example in examples:
        sections = split_sections(example["paper_text"])
        lexical = match_evidence(example["claim"], sections, limit=1)[0]
        semantic = match_evidence(
            example["claim"], sections, limit=1, semantic_matcher=matcher
        )[0]
        rows.append(
            {
                "id": example["id"],
                "lexical_section": lexical.section,
                "semantic_section": semantic.section,
                "expected_section": example["expected_section"],
                "lexical_correct": lexical.passage == example["expected_passage"],
                "semantic_correct": semantic.passage == example["expected_passage"],
            }
        )
    total = len(rows)
    percent = lambda count: round(100 * count / total, 2) if total else 0.0
    metrics = {
        "total_examples": total,
        "lexical_top_passage_accuracy_pct": percent(
            sum(row["lexical_correct"] for row in rows)
        ),
        "semantic_top_passage_accuracy_pct": percent(
            sum(row["semantic_correct"] for row in rows)
        ),
    }
    metrics["absolute_improvement_points"] = round(
        metrics["semantic_top_passage_accuracy_pct"]
        - metrics["lexical_top_passage_accuracy_pct"],
        2,
    )
    return rows, metrics


def calculate_nli_metrics(rows: list[dict], threshold: float = 0.65) -> dict:
    """Measure accuracy, class recall, and confidence-gated coverage."""
    total = len(rows)
    covered = [row for row in rows if row["confidence"] >= threshold]
    percent = lambda count, size: round(100 * count / size, 2) if size else 0.0
    metrics = {
        "total_examples": total,
        "accuracy_pct": percent(
            sum(row["actual_label"] == row["expected_label"] for row in rows), total
        ),
        "coverage_pct": percent(len(covered), total),
        "abstention_rate_pct": percent(total - len(covered), total),
        "covered_accuracy_pct": percent(
            sum(row["actual_label"] == row["expected_label"] for row in covered),
            len(covered),
        ),
        "false_entailment_rate_pct": percent(
            sum(row["actual_label"] == "entailment" for row in rows if row["expected_label"] != "entailment"),
            sum(row["expected_label"] != "entailment" for row in rows),
        ),
        "false_contradiction_rate_pct": percent(
            sum(row["actual_label"] == "contradiction" for row in rows if row["expected_label"] != "contradiction"),
            sum(row["expected_label"] != "contradiction" for row in rows),
        ),
    }
    for label in LABELS:
        expected = [row for row in rows if row["expected_label"] == label]
        metrics[f"{label}_recall_pct"] = percent(
            sum(row["actual_label"] == label for row in expected), len(expected)
        )
    return metrics


def nli_threshold_sweep(rows: list[dict]) -> list[dict]:
    """Show coverage and covered accuracy across candidate thresholds."""
    summaries = []
    for threshold in (0.5, 0.65, 0.75, 0.85, 0.9, 0.95):
        metrics = calculate_nli_metrics(rows, threshold)
        summaries.append({
            "threshold": threshold,
            "coverage_pct": metrics["coverage_pct"],
            "abstention_rate_pct": metrics["abstention_rate_pct"],
            "covered_accuracy_pct": metrics["covered_accuracy_pct"],
        })
    return summaries


def run_nli_benchmark(
    classifier: NLIClassifier | None = None,
    examples_path: Path = NLI_EXAMPLES_PATH,
    threshold: float = 0.65,
) -> tuple[list[dict], dict]:
    """Run a balanced, labelled evidence/claim NLI benchmark."""
    with examples_path.open(encoding="utf-8") as handle:
        examples = json.load(handle)
    classifier = classifier or NLIClassifier()
    rows = []
    for example in examples:
        prediction = classifier.predict(example["evidence"], example["claim"])
        rows.append(
            {
                "id": example["id"],
                "expected_label": example["expected_label"],
                "actual_label": prediction.label,
                "confidence": prediction.confidence,
                "above_threshold": prediction.confidence >= threshold,
            }
        )
    return rows, calculate_nli_metrics(rows, threshold)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare-matchers", action="store_true")
    parser.add_argument("--benchmark-nli", action="store_true")
    parser.add_argument("--analyze-nli", action="store_true")
    arguments = parser.parse_args()
    if arguments.analyze_nli:
        rows, metrics = run_nli_benchmark()
        for row in rows:
            if row["actual_label"] != row["expected_label"] or not row["above_threshold"]:
                print(f'{row["id"]}: expected={row["expected_label"]}, actual={row["actual_label"]}, confidence={row["confidence"]:.2%}')
        print("threshold_sweep:")
        for summary in nli_threshold_sweep(rows): print(summary)
        print("metrics:")
    elif arguments.benchmark_nli:
        _, metrics = run_nli_benchmark()
    elif arguments.compare_matchers:
        _, metrics = run_matcher_comparison()
    else:
        _,metrics=run_experiment()
    for key,value in metrics.items(): print(f"{key}: {value}")
