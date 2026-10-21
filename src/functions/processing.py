import json

from configs.paths import EXTRACTION_OUTPUT_PATH

with open(EXTRACTION_OUTPUT_PATH, "r") as f:
    extraction_log = json.load(f)

RAW_OUTPUTS = extraction_log["outputs"]

def _parse_extraction_outputs(outputs, confirmation=True) -> list[dict]:
    """
    Parse each paper's output string into entities/relations, per PMID.
    """

    parsed_extractions = []
    parse_failures = 0

    for item in outputs:
        try:
            parsed = json.loads(item["output"])
        except json.JSONDecodeError:
            parse_failures += 1
            parsed = {"entities": [], "relations": []}

        parsed_extractions.append({
            "pmid": item["pmid"],
            "entities": parsed.get("entities", []),
            "relations": parsed.get("relations", [])
        })

    if confirmation:
        print(f"Parsed {len(parsed_extractions)} extractions, {parse_failures} failed to parse as JSON.")

    return parsed_extractions

def _extractions_to_prediction_sets(parsed_extractions):
    """
    Flatten extractions into sets of tuples.
    """

    pred_ent = {
        (
            extraction["pmid"],
            ext["text"].strip().lower(),
            ext["type"]
        )
        for extraction in parsed_extractions
        for ext in extraction["entities"]
    }

    pred_rel = {
        (
            extraction["pmid"],
            rel["source"].strip().lower(),
            rel["relation"],
            rel["target"].strip().lower()
        )
        for extraction in parsed_extractions
        for rel in extraction["relations"]
    }

    return pred_ent, pred_rel

def process_outputs(confirmation=True):
    """
    Wrapper for final processing pipeline: takes raw `outputs` (pmid + JSON string per abstract)
    straight to eval-ready sets of tuples.

    Returns: (`pred_ent`, `pred_rel`)
    """

    parsed_extractions = _parse_extraction_outputs(outputs=RAW_OUTPUTS, confirmation=confirmation)
    pred_ent, pred_rel = _extractions_to_prediction_sets(parsed_extractions=parsed_extractions)

    return (pred_ent, pred_rel)