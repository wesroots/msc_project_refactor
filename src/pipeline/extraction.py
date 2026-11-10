import os

import pandas as pd
import time
import json

from openai import OpenAI, OpenAIError
from pathlib import Path

from configs.paths import PROMPT_TEMPLATE_PATH, BR_EXT_GUIDELINES_PATH, FS_BLOCK_PATH

MODEL_ID = "gpt-6-luna"

def _create_client() -> OpenAI:

    """
    Return OpenAI client.
    """

    API_KEY = os.getenv("OPEN_AI_KEY")

    client = OpenAI(
        api_key=API_KEY,
        timeout=120,
        max_retries=2
    )

    return client

def _load_prompt_template() -> str:

    """
    Load prompt template and return as string.
    """

    with open(PROMPT_TEMPLATE_PATH, "r") as f:
        prompt_template = f.read()

    return prompt_template

def conduct_extraction(output_path: Path, corpus: pd.DataFrame) -> dict:

    print("Loading extraction configurations...", end=" ", flush=True)

    # Create client
    client = _create_client()

    # Load BioRED-based extraction guidelines
    with open(BR_EXT_GUIDELINES_PATH, "r", encoding="utf-8") as f:
        br_ext_guidelines = f.read()

    # Load few-shot examples
    with open(FS_BLOCK_PATH, "r", encoding="utf-8") as f:
        fs_block = f.read()

    # Load prompt template
    prompt_template = _load_prompt_template()

    print("Done.")

    print("Beginning extraction...", end="", flush=True)

    start_time = time.perf_counter()

    outputs = []
    failures = []
    n_current_abstract = 1
    n_total_abstracts = corpus.shape[0]

    for _, row, in corpus.iterrows():
        abstract = row["abstract"]
        title = row["title"] if pd.notna(row["title"]) else ""

        prompt = (
            prompt_template
            .replace("{title}", title)
            .replace("{abstract}", abstract)
            .replace("{fs_block}", fs_block)
            .replace("{br_ext_guidelines}", br_ext_guidelines)
        )

        try:
            response = client.responses.create(
                model=MODEL_ID,
                input=prompt
            )
            outputs.append({
                "pmid": row["pmid"],
                "output": response.output_text,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.total_tokens
            })
        except OpenAIError as e:
            failures.append({
                "pmid": row["pmid"],
                "error": repr(e)
            })

        progress_time = time.perf_counter() - start_time
        avg_time_per_abstract = progress_time / n_current_abstract
        est_time_remaining = avg_time_per_abstract * (n_total_abstracts - n_current_abstract)
        rem_minutes = int(est_time_remaining // 60)
        rem_seconds = est_time_remaining % 60

        if rem_minutes and rem_seconds == 0:
            print(
                f"\rAbstract {n_current_abstract} of {n_total_abstracts} complete "
                f"({n_current_abstract / n_total_abstracts * 100:.1f})%; ",
                end= "",
                flush=True
            )
        else:
                print(
                f"\rAbstract {n_current_abstract} of {n_total_abstracts} complete "
                f"({n_current_abstract / n_total_abstracts * 100:.1f})%; "
                f"Est. time remaining: {rem_minutes}m {rem_seconds:.0f}s.",
                end= "",
                flush=True
            )

        n_current_abstract += 1

        extraction_log = {
            "model_id": MODEL_ID,
            "elapsed_time": time.perf_counter() - start_time,
            "outputs": outputs,
            "failures": failures
        }

    with open(output_path, "w") as f:
        json.dump(extraction_log, f, indent=2)

    print("")
    print(f"Extraction complete:\n - {len(outputs)} successes\n - {len(failures)} failures\n")
    print(F"Extraction log exported to '{output_path}'")

    return extraction_log