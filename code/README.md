# Multi-Domain Support Triage Agent

## Overview

This project is a terminal-based AI support triage system built for the HackerRank Orchestrate Hackathon.

It processes support tickets across three ecosystems:

- HackerRank
- Claude
- Visa

The system reads support tickets from CSV format, analyzes the issue, and generates structured outputs.

---

## Features

- Reads `support_tickets.csv`
- Detects product domain/company
- Identifies request type
- Routes tickets as `replied` or `escalated`
- Handles fraud, billing, bugs, access issues, feature requests
- Generates `output.csv`
- Produces transcript log

---

## Output Fields

For every ticket:

- `status`
- `product_area`
- `response`
- `justification`
- `request_type`

---

## Tech Stack

- Python
- pandas
- tqdm
- dotenv
- requests
- BeautifulSoup
- Gemini API

---

## Project Structure

``` id="ym4g35"
code/
├── main.py
├── agent.py
├── retriever.py
├── scraper.py
├── README.md