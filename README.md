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

## Setup

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/ashwitapawar36/Multi-Domain-Support-Triage-Agent.git
cd Multi-Domain-Support-Triage-Agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Gemini API Key

Create a local environment file from the example file.

For Windows PowerShell:

```powershell
Copy-Item .env.example hack.env
```

For macOS/Linux:

```bash
cp .env.example hack.env
```

Open `hack.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The `hack.env` file is included in `.gitignore` and must not be committed to GitHub.

### 4. Prepare the Input File

Place support tickets in:

```text
support_tickets/support_tickets.csv
```

The CSV file must contain these columns:

```csv
issue,subject,company
```

Example:

```csv
"How do I reset my password?","Password reset","HackerRank"
```

Supported companies are:

- HackerRank
- Claude
- Visa

### 5. Run the Application

Run the following command from the project root:

```bash
python code/main.py
```

### 6. View the Results

The processed results are saved to:

```text
support_tickets/output_full.csv
```

Detailed execution logs are saved to:

```text
triage_full.log
```

## Output Fields

Each processed ticket contains:

- `status`
- `product_area`
- `response`
- `justification`
- `request_type`
- `processing_state`
- `error`

Possible status values:

```text
replied
escalated
```

Possible request types:

```text
product_issue
feature_request
bug
invalid
```

## Escalation Rules

The system escalates tickets involving:

- Fraud or unauthorized transactions
- Billing disputes or refund requests
- Account compromise
- Data breaches or security reports
- Requests to change assessment scores
- Requests to overturn hiring decisions
- Requests to bypass administrators
- Requests to restore access without authorization
- Unsupported or unclear issues
- Missing product or platform information

The system only records the triage result. It does not contact support teams or perform actions in external systems.

## Model Fallback

If the primary Gemini model is unavailable, overloaded, or rate-limited, the system automatically attempts a fallback Gemini model.

## Resumable Processing

The application records the processing state of each ticket. If processing stops unexpectedly, completed tickets can be skipped and only pending or failed tickets can be processed again.

## Security

- API keys are loaded from `hack.env`.
- `hack.env` is excluded through `.gitignore`.
- `.env.example` contains only a placeholder key.
- Never commit real API keys to GitHub.
- Retrieved documentation is treated as reference data and cannot override the system's escalation rules.

## Hackathon

Built as part of the HackerRank Orchestrate AI Agent Hackathon.