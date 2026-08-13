"""Run the labelled safety and semantic-retrieval benchmarks."""
import argparse
import csv
import json
from pathlib import Path
from src.academic import match_evidence, split_sections
from src.config import EXPERIMENT_RESULTS_PATH, SEMANTIC_EXAMPLES_PATH
from src.evaluator import evaluate_answer
from src.example_data import load_examples,validate_examples
from src.models import EvaluationInput
from src.semantic import SemanticMatcher

def calculate_metrics(rows:list[dict])->dict:
    total=len(rows); unsafe=[r for r in rows if r["expected_decision"]!="PUBLISH"]
    unsupported=[r for r in rows if r["expected_claim_label"]=="UNSUPPORTED"]
    contradicted=[r for r in rows if r["expected_claim_label"]=="CONTRADICTED"]
    pct=lambda n,d: round(100*n/d,2) if d else 0.0
    return {"total_examples":total,"decision_accuracy_pct":pct(sum(r["expected_decision"]==r["actual_decision"] for r in rows),total),"unsupported_detection_rate_pct":pct(sum(r["actual_claim_label"]=="UNSUPPORTED" for r in unsupported),len(unsupported)),"contradiction_detection_rate_pct":pct(sum(r["actual_claim_label"]=="CONTRADICTED" for r in contradicted),len(contradicted)),"false_publish_rate_pct":pct(sum(r["actual_decision"]=="PUBLISH" for r in unsafe),len(unsafe)),"review_rate_pct":pct(sum(r["actual_decision"]=="REVIEW" for r in rows),total)}

def run_experiment(path:Path=EXPERIMENT_RESULTS_PATH,write_output:bool=True):
    examples=load_examples(); errors=validate_examples(examples)
    if errors: raise ValueError("; ".join(errors))
    rows=[]
    for item in examples:
        result=evaluate_answer(EvaluationInput(item["question"],item["paper_text"],item["answer"]))
        rows.append({"id":item["id"],"category":item["category"],"expected_claim_label":item["expected_claim_label"],"actual_claim_label":result.claim_results[0].label.value,"expected_decision":item["expected_decision"],"actual_decision":result.final_decision.value})
    if write_output:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("w",newline="",encoding="utf-8") as handle:
            writer=csv.DictWriter(handle,fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
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

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare-matchers", action="store_true")
    arguments = parser.parse_args()
    if arguments.compare_matchers:
        _, metrics = run_matcher_comparison()
    else:
        _,metrics=run_experiment()
    for key,value in metrics.items(): print(f"{key}: {value}")
