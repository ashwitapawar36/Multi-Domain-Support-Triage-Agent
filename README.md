# Multi-Domain Support Triage Agent

A terminal-based AI support triage system built for the HackerRank Orchestrate Hackathon.

The system processes customer-support tickets across three domains:

- HackerRank
- Claude
- Visa

It retrieves relevant documentation from a local support corpus and uses the Gemini API to classify tickets, generate grounded responses, and determine whether human escalation is required.

## Features

- Support-ticket classification
- Product-area identification
- Request-type detection
- BM25-based documentation retrieval
- Retrieval-Augmented Generation (RAG)
- Gemini API integration
- Corpus-grounded responses
- Safety-aware escalation rules
- Fallback model handling for API failures
- Resumable ticket processing
- Batch CSV processing
- Structured CSV output
- Detailed execution logs

## Workflow

1. Read support tickets from a CSV file.
2. Load the local support documentation corpus.
3. Retrieve relevant documents using BM25-style matching.
4. Send the ticket and retrieved documentation to Gemini.
5. Generate a structured JSON triage result.
6. Apply deterministic escalation safeguards.
7. Save the result to a CSV file.
8. Record processing details in a log file.

## Technologies Used

- Python
- Gemini API
- Retrieval-Augmented Generation
- BM25 Retrieval
- Prompt Engineering
- CSV Processing

## Project Structure

```text
Multi-Domain-Support-Triage-Agent/
│
├── code/
│   ├── agent.py
│   ├── main.py
│   ├── retriever.py
│   └── scraper.py
│
├── data/
│   ├── hackerrank/
│   ├── claude/
│   └── visa/
│
├── support_tickets/
│   ├── support_tickets.csv
│   └── output_full.csv
│
├── .env.example
├── .gitignore
├── hack.env
├── requirements.txt
├── README.md
└── triage_full.log