"""Academic benchmark loader and schema validation."""
import json
from pathlib import Path
from src.config import EVALUATION_EXAMPLES_PATH
from src.models import ClaimLabel, Decision

REQUIRED={"id","category","question","paper_text","answer","expected_claim_label","expected_decision"}

def load_examples(path: Path=EVALUATION_EXAMPLES_PATH)->list[dict]:
    with path.open(encoding="utf-8") as handle: return json.load(handle)

def validate_examples(examples: object)->list[str]:
    if not isinstance(examples,list): return ["Benchmark must be a list."]
    errors=[]; ids=[]
    for index,item in enumerate(examples,1):
        if not isinstance(item,dict): errors.append(f"Example {index} must be an object."); continue
        missing=REQUIRED-set(item)
        if missing: errors.append(f"Example {index} missing: {', '.join(sorted(missing))}"); continue
        ids.append(item["id"])
        if item["expected_claim_label"] not in {x.value for x in ClaimLabel}: errors.append(f"Example {index} has invalid claim label.")
        if item["expected_decision"] not in {x.value for x in Decision}: errors.append(f"Example {index} has invalid decision.")
    if len(ids)!=len(set(ids)): errors.append("Benchmark IDs must be unique.")
    if len(examples)<50: errors.append("Benchmark requires at least 50 labelled examples.")
    return errors
