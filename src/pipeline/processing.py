import json

from configs.paths import NEW_EXT_OUTPUT_PATH

with open(NEW_EXT_OUTPUT_PATH, "r") as f:
    extraction_log = json.load(f)

RAW_OUTPUTS = extraction_log["outputs"]

def _parse_extraction_outputs(outputs) -> tuple[list[dict], int]:
    """
    Parse each paper's extraction string (from outputs list) into entities/relations, per PMID.

    Returns:
    {
        "pmid" : [],
        "entities": [],
        "relations": []
    }
    """

    print("Parsing each record's extraction string into list[dict] form...", end=" ", flush=True)

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

    print("Done.")

    return (parsed_extractions, parse_failures)

def _extractions_to_prediction_sets(parsed_extractions):
    """
    Flatten extractions into sets of tuples.
    """

    print("Flattening extractions into sets of tuples...", end=" ", flush=True)

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

    print("Done.")

    return pred_ent, pred_rel

def process_outputs():
    """
    Wrapper for final processing pipeline: takes raw `outputs` (pmid + JSON string per abstract)
    straight to eval-ready sets of tuples.

    Returns: (`pred_ent`, `pred_rel`)
    """
    parsed_extractions, parse_failures = _parse_extraction_outputs(outputs=RAW_OUTPUTS)
    pred_ent, pred_rel = _extractions_to_prediction_sets(parsed_extractions=parsed_extractions)

    print(f"\nProccessing complete:\n - {parse_failures} failures")

    return (pred_ent, pred_rel)