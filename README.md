# Multi-Domain Support Triage Agent

A terminal-based AI support triage system built for the HackerRank Orchestrate Hackathon.

The agent processes customer support tickets across three ecosystems:

* HackerRank
* Claude
* Visa

Using only a provided support knowledge base, the system classifies tickets, retrieves relevant documentation, determines whether an issue can be answered safely, and decides when escalation to a human agent is required.

## Features

* Support ticket classification
* Product area identification
* Request type detection
* Retrieval-Augmented Generation (RAG)
* Safety-aware escalation logic
* Corpus-grounded responses
* Batch CSV processing
* Terminal-based execution

## Workflow

1. Load support corpus
2. Classify incoming ticket
3. Retrieve relevant support documents
4. Determine escalation requirements
5. Generate grounded response
6. Export results to CSV

## Project Structure

```text
code/
├── agent.py
├── retriever.py
├── scraper.py
├── main.py
└── README.md

corpus/
├── HackerRank.txt
├── Claude.txt
└── Visa.txt

support_tickets/
├── support_tickets.csv
└── output.csv
```

## Technologies Used

* Python
* Retrieval-Augmented Generation (RAG)
* Vector Search / Similarity Retrieval
* CSV Processing
* Prompt Engineering

## Running the Project

```bash
python code/main.py
```

The generated predictions will be written to:

```text
support_tickets/output.csv
```

## Supported Domains

* HackerRank Support
* Claude Help Center
* Visa Consumer Support

## Key Design Goals

* Grounded responses only
* No unsupported policy claims
* Safe handling of sensitive requests
* Human escalation for high-risk cases
* Deterministic and reproducible outputs

## Hackathon

Built as part of the HackerRank Orchestrate AI Agent Hackathon.
