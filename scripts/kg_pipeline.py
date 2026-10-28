from src.pipeline.corpus import construct_corpus
from src.pipeline.extraction import conduct_extraction

from configs.paths import NEW_CORPUS_OUTPUT_PATH, NEW_EXT_OUTPUT_PATH

# Assemble corpus
print("----- ASSEMBLING CORPUS -----")
corpus = construct_corpus(save_path=NEW_CORPUS_OUTPUT_PATH)
print("----- CORPUS ASSEMBLED -----\n")


# Conduct extraction
print("----- PERFORMING EXTRACTION -----")
extraction_log = conduct_extraction(output_path=NEW_EXT_OUTPUT_PATH, corpus=corpus)
print("----- EXTRACTION COMPLETE -----\n")

# Validate (NEN, OV)


# Construct KG