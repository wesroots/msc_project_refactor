import os

from Bio import Entrez
from pathlib import Path

import pandas as pd

from configs.queries import N_RETURNED_ARTICLES, QUERIES

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")

def _fetch_papers(query, num_articles=N_RETURNED_ARTICLES):

    Entrez.email = EMAIL_ADDRESS

    search_handle = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=num_articles
    )

    search_results = Entrez.read(search_handle)
    search_handle.close()

    ids = search_results["IdList"]

    if not ids:
        return {"PubmedArticle": []}

    fetch_handle = Entrez.efetch(
        db="pubmed",
        id=",".join(ids),
        rettype="abstract",
        retmode="xml"
    )

    papers = Entrez.read(fetch_handle)
    fetch_handle.close()

    return papers

def construct_corpus(save_path: Path, save: bool=True):

    q_papers = []

    for query in QUERIES:
        q_papers.append(_fetch_papers(query))

    records = []
    for result in q_papers:
        for paper in result["PubmedArticle"]:
            citation = paper["MedlineCitation"]
            article = citation["Article"]

            abstract_parts = article.get("Abstract", {}).get("AbstractText", [])

            records.append({
                "pmid": str(citation["PMID"]),
                "title": str(article.get("ArticleTitle", "")) or None,
                "abstract": " ".join(str(part) for part in abstract_parts) or None,
            })

    corpus = (
        pd.DataFrame(records)
        .drop_duplicates(subset="pmid")
        .dropna(subset=["abstract"])
    )

    if save:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        corpus.to_csv(save_path, index=False)

    return corpus