from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DISS_CORPUS_OUTPUT_PATH = PROJECT_ROOT / "data/thesis/corpus.csv"
DISS_EXT_OUTPUT_PATH = PROJECT_ROOT / "data/thesis/extraction_log.json"

NEW_CORPUS_OUTPUT_PATH = PROJECT_ROOT / "data/run/corpus.csv"
NEW_EXT_OUTPUT_PATH = PROJECT_ROOT / "data/run/extraction_log.json"

PROMPT_TEMPLATE_PATH = PROJECT_ROOT / "data/prompt_template.txt"
BR_EXT_GUIDELINES_PATH = PROJECT_ROOT / "data/br_ext_guidelines.txt"
FS_BLOCK_PATH = PROJECT_ROOT / "data/fs_block.txt"