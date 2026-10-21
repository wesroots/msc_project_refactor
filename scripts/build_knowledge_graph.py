from src.functions.corpus import construct_corpus
from src.functions.extraction import conduct_extraction

from configs.paths import NEW_CORPUS_OUTPUT_PATH, NEW_EXT_OUTPUT_PATH

# Assemble corpus
corpus = construct_corpus(save_path=NEW_CORPUS_OUTPUT_PATH)

# Conduct extraction
extraction_log = conduct_extraction(output_path=NEW_EXT_OUTPUT_PATH, corpus=corpus)

# Validate (NEN, OV)


# Construct KG