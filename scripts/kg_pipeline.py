from src.pipeline.corpus import construct_corpus
from src.pipeline.extraction import conduct_extraction
from src.pipeline.processing import process_outputs

from configs.paths import NEW_CORPUS_OUTPUT_PATH, NEW_EXT_OUTPUT_PATH

# ----- Assemble corpus -----
print("<ASSEMBLING CORPUS>")
corpus = construct_corpus(save_path=NEW_CORPUS_OUTPUT_PATH)
print("")

# ----- Conduct extraction -----
print("<PERFORMING EXTRACTION>")
extraction_log = conduct_extraction(output_path=NEW_EXT_OUTPUT_PATH, corpus=corpus)
print("")

# ----- Process extractions -----
print("<PROCESSING EXTRACTIONS>")
pred_ent, pred_rel = process_outputs()
print("")

# ----- Validate (NEN, OV) -----
print("<VALIDATING PREDICTIONS>")

# ----- Construct KG -----