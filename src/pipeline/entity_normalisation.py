import os
import requests
import re
import time

NCBI_EMAIL = os.getenv("EMAIL_ADDRESS")
NCBI_API_KEY = None

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
CELLOSAURUS_BASE = "https://api.cellosaurus.org/search/cell-line"

REQUEST_DELAY = 0.34

RSID_PATTERN = re.compile(r"^rs\d+$", re.IGNORECASE)

def _eutils_esearch(db, term):
    params = {"db": db, "term": term, "retmode": "json", "retmax": 1}

    if NCBI_EMAIL:
        params["email"] = NCBI_EMAIL
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    resp = requests.get(EUTILS_BASE + "esearch.fcgi", params=params, timeout=15)
    resp.raise_for_status()
    time.sleep(REQUEST_DELAY)

    return resp.json().get("esearchresult", {}).get("idlist", [])

# ----- Gene entity -----
def _normalise_gene(text):
    ids = _eutils_esearch("gene", f"{text}[sym]")

    if not ids:
        ids = _eutils_esearch("gene", text)
    if not ids:
        return {"normalised_id": None, "source": "NCBI Gene", "resolved": False, "note": "no match"}

    return {"normalised_id": f"NCBIGene:{ids[0]}", "source": "NCBI Gene", "resolved": True, "note": None}

# ----- MeSH entity -----
def _normalise_mesh(text):
    ids = _eutils_esearch("mesh", text)

    if not ids:
        return {"normalised_id": None, "source": "MeSH", "resolved": False, "note": "no match"}

    return {"normalised_id": f"MeSH:{ids[0]}", "source": "MeSH", "resolved": True, "note": None}

# ----- Taxon entity -----
def _normalise_taxon(text):
    ids = _eutils_esearch("taxonomy", text)

    if not ids:
        return {"normalised_id": None, "source": "NCBI Taxonomy", "resolved": False, "note": "no match"}

    return {"normalised_id": f"NCBITaxon:{ids[0]}", "source": "NCBI Taxonomy", "resolved": True, "note": None}

# ----- Cell line entity -----
def _normalise_cellline(text):
    try:
        params = {"q": text, "format": "json", "fields": "ac", "rows": 1}
        resp = requests.get(CELLOSAURUS_BASE, params=params, timeout=15)
        resp.raise_for_status()
        time.sleep(REQUEST_DELAY)
        results = resp.json().get("Cellosaurus", {}).get("cell-line-list", [])

        if not results:
            return {"normalised_id": None, "source": "Cellosaurus", "resolved": False, "note": "no match"}

        accession_list = results[0].get("accession-list", [])
        primary = next((a["value"] for a in accession_list if a.get("type") == "primary"), None)
        if not primary and accession_list:
            primary = accession_list[0].get("value")  # fallback: take the first one if no "primary" flagged

        if not primary:
            return {"normalised_id": None, "source": "Cellosaurus", "resolved": False,
                    "note": "match found but accession missing -- check response shape"}

        return {"normalised_id": f"Cellosaurus:{primary}", "source": "Cellosaurus", "resolved": True, "note": None}
    except requests.RequestException as e:
        return {"normalised_id": None, "source": "Cellosaurus", "resolved": False, "note": f"request error: {e}"}

# ----- Variant entity -----
def _normalise_variant(text):
    """rsIDs only -- see module docstring for why free-text HGVS is out of scope."""
    cleaned = text.strip().lower()
    if RSID_PATTERN.match(cleaned):
        return {"normalised_id": f"dbSNP:{cleaned}", "source": "dbSNP", "resolved": True, "note": None}
    return {"normalised_id": None, "source": "unresolved", "resolved": False,
            "note": "free-text variant notation lacks a transcript/genomic accession"}

NORMALISERS = {
    "GeneOrGeneProduct": _normalise_gene,
    "ChemicalEntity": _normalise_mesh,
    "DiseaseOrPhenotypicFeature": _normalise_mesh,
    "OrganismTaxon": _normalise_taxon,
    "CellLine": _normalise_cellline,
    "SequenceVariant": _normalise_variant,
}

# ----- Normalise entity wrapper -----
def _normalise_entity(text, entity_type):
    normaliser = NORMALISERS.get(entity_type)
    if normaliser is None:
        result = {"normalised_id": None, "source": "unsupported", "resolved": False,
                   "note": f"no normaliser registered for type '{entity_type}'"}
    else:
        result = normaliser(text)

    return result

def _scope_entities():
    pass

def run_normalisation():
    results = []

    for i, row in unique_to_normalise.iterrows():
        results = _normalise_entity(row["text"], row["type"])