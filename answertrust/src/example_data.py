"""Versioned benchmark loading and provenance-aware validation."""
import json
from pathlib import Path
from src.config import EVALUATION_EXAMPLES_PATH
from src.models import ClaimLabel, Decision

CORE_REQUIRED={"id","category","question","paper_text","answer","expected_claim_label","expected_decision"}
METADATA_REQUIRED={"schema_version","source_type","source_title","source_locator","reuse_license","excerpt_section","difficulty_category","annotation_status","reviewer_label","reviewer_confidence","label_rationale"}
DIFFICULTIES={"BASIC","INTERMEDIATE","HARD"}
ANNOTATION_STATUSES={"PROJECT_AUTHORED","INDEPENDENTLY_REVIEWED"}

def load_examples(path:Path=EVALUATION_EXAMPLES_PATH)->list[dict]:
    """Load examples and apply declared dataset-level metadata defaults."""
    with path.open(encoding="utf-8") as handle: examples=json.load(handle)
    sources_path=path.with_name("evaluation_sources.json")
    sources={}
    if sources_path.exists():
        with sources_path.open(encoding="utf-8") as handle:
            sources={item["id"]:item for item in json.load(handle)}
    manifest_path=path.with_name(f"{path.stem}.manifest.json")
    if not manifest_path.exists(): return examples
    with manifest_path.open(encoding="utf-8") as handle: manifest=json.load(handle)
    defaults=manifest.get("example_defaults",{}); normalized=[]
    for item in examples:
        source=sources.get(item.get("source_ref"),{})
        enriched={**defaults,**source,**item}; enriched["schema_version"]=manifest["schema_version"]
        if source:
            enriched["source_type"]="REAL_EXCERPT"
            enriched.setdefault("annotation_status","PROJECT_AUTHORED")
        elif item.get("source_ref"):
            enriched["source_type"]="UNKNOWN_SOURCE"
        enriched.setdefault("source_locator",item.get("id",""))
        enriched.setdefault("excerpt_section",_first_section(item.get("paper_text","")))
        enriched.setdefault("reviewer_label",item.get("expected_claim_label"))
        enriched.setdefault("label_rationale",f"Project-created {item.get('category','regression')} safety case.")
        normalized.append(enriched)
    return normalized

def validate_examples(examples:object)->list[str]:
    if not isinstance(examples,list): return ["Benchmark must be a list."]
    errors=[]; ids=[]; claim_labels={item.value for item in ClaimLabel}; decisions={item.value for item in Decision}
    for index,item in enumerate(examples,1):
        if not isinstance(item,dict): errors.append(f"Example {index} must be an object."); continue
        missing=(CORE_REQUIRED|METADATA_REQUIRED)-set(item)
        if missing: errors.append(f"Example {index} missing: {', '.join(sorted(missing))}"); continue
        ids.append(item["id"])
        if item["schema_version"]!=2: errors.append(f"Example {index} must use schema version 2.")
        if item["expected_claim_label"] not in claim_labels or item["reviewer_label"] not in claim_labels: errors.append(f"Example {index} has an invalid claim label.")
        if item["expected_decision"] not in decisions: errors.append(f"Example {index} has an invalid decision.")
        if item["difficulty_category"] not in DIFFICULTIES: errors.append(f"Example {index} has an invalid difficulty category.")
        if item["annotation_status"] not in ANNOTATION_STATUSES: errors.append(f"Example {index} has an invalid annotation status.")
        confidence=item["reviewer_confidence"]
        if not isinstance(confidence,(int,float)) or not 0<=confidence<=1: errors.append(f"Example {index} reviewer confidence must be between 0 and 1.")
        if not str(item["label_rationale"]).strip(): errors.append(f"Example {index} requires a label rationale.")
        if item["source_type"]=="REAL_EXCERPT":
            for field in ("source_title","source_locator","reuse_license","excerpt_section"):
                if not str(item[field]).strip(): errors.append(f"Example {index} real excerpt requires {field}.")
        elif item["source_type"]!="SYNTHETIC": errors.append(f"Example {index} has an invalid source type.")
    if len(ids)!=len(set(ids)): errors.append("Benchmark IDs must be unique.")
    if len(examples)<50: errors.append("Benchmark requires at least 50 labelled examples.")
    return errors

def _first_section(paper_text:str)->str:
    first_line=paper_text.splitlines()[0].strip() if paper_text else ""
    return first_line if first_line.isupper() else "UNSPECIFIED"
