#!/usr/bin/env python3
"""
Fetch latest GLP-1 research papers from PubMed E-utilities API.
Targets Q1/Q2 journals and covers GLP-1RA, obesity, diabetes, and extension topics.
"""

import json
import sys
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import quote_plus

PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

JOURNALS_Q1 = [
    "Diabetes Care",
    "Diabetes Obesity and Metabolism",
    "Obesity",
    "International Journal of Obesity",
    "Obesity Reviews",
    "Current Obesity Reports",
    "Diabetes",
    "Diabetes and Metabolism",
    "Diabetes Metabolism Research and Reviews",
    "Journal of Clinical Endocrinology and Metabolism",
    "BMJ Open Diabetes Research and Care",
    "Diabetes Technology and Therapeutics",
]

JOURNALS_Q2 = [
    "Diabetes Therapy",
    "Journal of Diabetes",
    "Obesity Science and Practice",
    "Clinical Obesity",
    "Obesity Research and Clinical Practice",
    "Obesity Medicine",
    "JMIR Diabetes",
]

ALL_JOURNALS = JOURNALS_Q1 + JOURNALS_Q2

GLP1_CORE = (
    '("GLP-1"[Title/Abstract] OR "GLP-1 receptor agonist"[Title/Abstract] '
    "OR GLP-1RA[Title/Abstract] OR semaglutide[Title/Abstract] "
    "OR liraglutide[Title/Abstract] OR dulaglutide[Title/Abstract] "
    "OR exenatide[Title/Abstract] OR lixisenatide[Title/Abstract] "
    "OR tirzepatide[Title/Abstract] OR incretin[Title/Abstract])"
)

HEADERS = {"User-Agent": "GLP1BrainBot/1.0 (research aggregator)"}


def build_queries(days: int = 7) -> list[str]:
    lookback = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y/%m/%d")
    date_part = f'"{lookback}"[Date - Publication] : "3000"[Date - Publication]'

    topics = [
        'obesity[Title/Abstract] OR overweight[Title/Abstract] OR "weight loss"[Title/Abstract]',
        '"type 2 diabetes"[Title/Abstract] OR T2D[Title/Abstract] OR T2DM[Title/Abstract]',
        'cardiovascular[Title/Abstract] OR MACE[Title/Abstract] OR "heart failure"[Title/Abstract]',
        "MASLD[Title/Abstract] OR MASH[Title/Abstract] OR NAFLD[Title/Abstract] OR NASH[Title/Abstract]",
        '"chronic kidney disease"[Title/Abstract] OR CKD[Title/Abstract]',
        '"sleep apnea"[Title/Abstract] OR OSA[Title/Abstract]',
        '"chronic pain"[Title/Abstract] OR fibromyalgia[Title/Abstract]',
        'tinnitus[Title/Abstract] OR dizziness[Title/Abstract] OR "brain fog"[Title/Abstract]',
        "depression[Title/Abstract] OR anxiety[Title/Abstract] OR cognition[Title/Abstract]",
        'addiction[Title/Abstract] OR alcohol[Title/Abstract] OR "binge eating"[Title/Abstract]',
        'aging[Title/Abstract] OR longevity[Title/Abstract] OR "anti-aging"[Title/Abstract]',
    ]

    queries = []
    for topic in topics:
        queries.append(f"{GLP1_CORE} AND ({topic}) AND {date_part}")

    journal_part = " OR ".join([f'"{j}"[Journal]' for j in ALL_JOURNALS])
    queries.append(f"({journal_part}) AND {GLP1_CORE} AND {date_part}")

    return queries


def search_papers(query: str, retmax: int = 20) -> list[str]:
    params = (
        f"?db=pubmed&term={quote_plus(query)}&retmax={retmax}&sort=date&retmode=json"
    )
    url = PUBMED_SEARCH + params
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"[ERROR] PubMed search failed: {e}", file=sys.stderr)
        return []


def fetch_details(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    ids = ",".join(pmids)
    params = f"?db=pubmed&id={ids}&retmode=xml"
    url = PUBMED_FETCH + params
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=60) as resp:
            xml_data = resp.read().decode()
    except Exception as e:
        print(f"[ERROR] PubMed fetch failed: {e}", file=sys.stderr)
        return []

    papers = []
    try:
        root = ET.fromstring(xml_data)
        for article in root.findall(".//PubmedArticle"):
            medline = article.find(".//MedlineCitation")
            art = medline.find(".//Article") if medline else None
            if art is None:
                continue

            title_el = art.find(".//ArticleTitle")
            title = (
                (title_el.text or "").strip()
                if title_el is not None and title_el.text
                else ""
            )
            if not title:
                continue

            abstract_parts = []
            for abs_el in art.findall(".//Abstract/AbstractText"):
                label = abs_el.get("Label", "")
                text = "".join(abs_el.itertext()).strip()
                if label and text:
                    abstract_parts.append(f"{label}: {text}")
                elif text:
                    abstract_parts.append(text)
            abstract = " ".join(abstract_parts)[:2000]

            journal_el = art.find(".//Journal/Title")
            journal = (
                (journal_el.text or "").strip()
                if journal_el is not None and journal_el.text
                else ""
            )

            pub_date = art.find(".//PubDate")
            date_str = ""
            if pub_date is not None:
                year = pub_date.findtext("Year", "")
                month = pub_date.findtext("Month", "")
                day = pub_date.findtext("Day", "")
                parts = [p for p in [year, month, day] if p]
                date_str = " ".join(parts)

            pmid_el = medline.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else ""
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

            keywords = []
            for kw in medline.findall(".//KeywordList/Keyword"):
                if kw.text:
                    keywords.append(kw.text.strip())

            authors = []
            for author in art.findall(".//AuthorList/Author"):
                last = author.findtext("LastName", "")
                fore = author.findtext("ForeName", "")
                if last:
                    authors.append(f"{last} {fore}".strip())

            papers.append(
                {
                    "pmid": pmid,
                    "title": title,
                    "journal": journal,
                    "date": date_str,
                    "abstract": abstract,
                    "url": link,
                    "keywords": keywords,
                    "authors": authors[:5],
                }
            )
    except ET.ParseError as e:
        print(f"[ERROR] XML parse failed: {e}", file=sys.stderr)

    return papers


def main():
    parser = argparse.ArgumentParser(description="Fetch GLP-1 papers from PubMed")
    parser.add_argument("--days", type=int, default=7, help="Lookback days")
    parser.add_argument(
        "--max-papers", type=int, default=40, help="Max papers to fetch"
    )
    parser.add_argument("--output", default="-", help="Output file (- for stdout)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    queries = build_queries(days=args.days)
    all_pmids = set()

    for i, query in enumerate(queries):
        print(f"[INFO] Running query {i + 1}/{len(queries)}...", file=sys.stderr)
        pmids = search_papers(query, retmax=15)
        all_pmids.update(pmids)
        print(
            f"  Found {len(pmids)} new PMIDs (total unique: {len(all_pmids)})",
            file=sys.stderr,
        )

    pmid_list = list(all_pmids)[: args.max_papers]
    print(f"[INFO] Fetching details for {len(pmid_list)} papers...", file=sys.stderr)

    if not pmid_list:
        print("NO_CONTENT", file=sys.stderr)
        if args.json:
            print(
                json.dumps(
                    {
                        "date": datetime.now(timezone(timedelta(hours=8))).strftime(
                            "%Y-%m-%d"
                        ),
                        "count": 0,
                        "papers": [],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        return

    papers = fetch_details(pmid_list)
    print(f"[INFO] Fetched details for {len(papers)} papers", file=sys.stderr)

    output_data = {
        "date": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d"),
        "count": len(papers),
        "papers": papers,
    }

    out_str = json.dumps(output_data, ensure_ascii=False, indent=2)

    if args.output == "-":
        print(out_str)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)
        print(f"[INFO] Saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
