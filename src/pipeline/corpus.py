import os

from Bio import Entrez
from pathlib import Path

import pandas as pd

from configs.queries import N_RETURNED_ARTICLES, QUERIES

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
Entrez.email = EMAIL_ADDRESS

def _fetch_papers(query, db, num_articles=N_RETURNED_ARTICLES) -> dict:

    # ----- Search query on PubMed -----
    search_handle = Entrez.esearch(
        db=db,
        term=query,
        retmax=num_articles
    )

    # ----- Parse returned `search_handle` raw XML to dict-like Python object -----
    search_results = Entrez.read(search_handle)
    search_handle.close()

    # ----- Get PMIDs -----
    ids = search_results["IdList"]

    # ----- If search found nothing, return empty list -----
    if not ids:
        return {"PubmedArticle": []}

    # ----- Fetch PubMed article records -----
    fetch_handle = Entrez.efetch(
        db="pubmed",
        id=",".join(ids),
        rettype="abstract",
        retmode="xml"
    )

    # ----- Parse papers from XML into dict-like Python object -----
    papers = Entrez.read(fetch_handle)
    fetch_handle.close()

    return papers

def construct_corpus(save_path: Path, db="pubmed", save: bool=True):

    # ----- Initiate list of result dictionaries -----
    query_papers = []

    # ----- Fetch and append result dictionary to list -----
    print(f"Fetching papers...", end=" ", flush=True)
    for query in QUERIES:
        query_papers.append(_fetch_papers(query, db))
    print("Done.")

    print("Parsing to DataFrame...", end=" ", flush=True)
    # ----- Parse from list of returned dictionaries to list of dictionaries of each returned record -----
    records = []
    for result in query_papers:
        for paper in result["PubmedArticle"]:
            citation = paper["MedlineCitation"]
            article = citation["Article"]

            abstract_parts = article.get("Abstract", {}).get("AbstractText", [])

            records.append({
                "pmid": str(citation["PMID"]),
                "title": str(article.get("ArticleTitle", "")) or None,
                "abstract": " ".join(str(part) for part in abstract_parts) or None,
            })

    # ----- Convert list of record dictionaries into a pandas DataFrame -----
    corpus = (
        pd.DataFrame(records)
        .drop_duplicates(subset="pmid")
        .dropna(subset=["abstract"])
    )

    print("Done.")

    # ----- Save by default -----
    if save:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        corpus.to_csv(save_path, index=False)
        print("")
        print(f"Exported corpus to '{save_path}'.")
        return corpus

    print("")
    print("Corpus not exported.")

    return corpus