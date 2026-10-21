QUERY_TEMPLATE = [
    '("gene"[Title/Abstract] OR "protein"[Title/Abstract])',
    '("disease"[Title/Abstract] OR "disorder"[Title/Abstract])',
    '("drug"[Title/Abstract] OR "chemical"[Title/Abstract])',
    '("variant"[Title/Abstract] OR "mutation"[Title/Abstract])',
    '"gene"[Title/Abstract] AND "disease"[Title/Abstract]',
    '"drug"[Title/Abstract] AND "disease"[Title/Abstract]',
    '"gene"[Title/Abstract] AND "drug"[Title/Abstract]',
    '"variant"[Title/Abstract] AND "disease"[Title/Abstract]'
]

QUERY_YEAR_RANGE = range(2024, 2027)

QUERIES = [
    f'{q} AND "{year}"[Date - Publication]'
    for q in QUERY_TEMPLATE
    for year in QUERY_YEAR_RANGE
]

N_RETURNED_ARTICLES = 25