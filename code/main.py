import pandas as pd
import os
import sys
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(dotenv_path="../hack.env")

from scraper import build_corpus, load_corpus
from retriever import retrieve
from agent import triage_ticket

INPUT_FILE  = "../support_tickets/support_tickets.csv"
OUTPUT_FILE = "../support_tickets/output.csv"
LOG_FILE    = "../log.txt"

def main():
    print("=== Step 1: Loading support corpus ===")
    corpus = load_corpus()
    if not corpus:
        print("No corpus found. Scraping support sites...")
        corpus = build_corpus()
    else:
        print(f"Loaded corpus for: {list(corpus.keys())}")

    print(f"\n=== Step 2: Reading {INPUT_FILE} ===")
    df = pd.read_csv(INPUT_FILE)
    print(f"Found {len(df)} tickets")

    results = []

    print("\n=== Step 3: Triaging tickets ===")
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write("=== SUPPORT TRIAGE AGENT LOG ===\n")

        for i, row in tqdm(df.iterrows(), total=len(df)):
            issue   = str(row.get("issue", ""))
            subject = str(row.get("subject", ""))
            company = str(row.get("company", "None")).strip()
            if company == "None" or company == "nan":
                company = None

            docs = retrieve(issue, company, corpus)

            log.write(f"\n{'='*60}\nTicket #{i+1} | Company: {company}\nSubject: {subject}\nIssue: {issue[:200]}\n")
            result = triage_ticket(issue, subject, company, docs, log_file=log)

            results.append(result)

    print(f"\n=== Step 4: Saving to {OUTPUT_FILE} ===")
    output_df = df.copy()
    output_df["status"]        = [r.get("status", "escalated") for r in results]
    output_df["product_area"]  = [r.get("product_area", "") for r in results]
    output_df["response"]      = [r.get("response", "") for r in results]
    output_df["justification"] = [r.get("justification", "") for r in results]
    output_df["request_type"]  = [r.get("request_type", "product_issue") for r in results]

    output_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Done! Output saved to {OUTPUT_FILE}")
    print(f"Transcript saved to {LOG_FILE}")

if __name__ == "__main__":
    main()