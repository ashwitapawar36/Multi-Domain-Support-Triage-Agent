import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "support_tickets" / "support_tickets.csv"
OUTPUT_FILE = ROOT / "support_tickets" / "output_full.csv"
LOG_FILE = ROOT / "triage_full.log"

# Keep True until we have checked CSV reading and corpus loading.
CHECK_INPUT_ONLY = False

RESULT_FIELDS = [
    "status",
    "product_area",
    "response",
    "justification",
    "request_type",
]


def read_tickets():
    with INPUT_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("The CSV is empty or has no header.")

        columns = [
            name.strip().lower() for name in reader.fieldnames
        ]

        if len(columns) != len(set(columns)):
            raise ValueError("The CSV has duplicate column names.")

        required = {"issue", "subject", "company"}
        missing = required - set(columns)

        if missing:
            raise ValueError(
                f"Missing CSV columns: {sorted(missing)}"
            )

        reader.fieldnames = columns
        tickets = []

        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(
                    f"CSV row {row_number} has extra values. "
                    "Check commas and quotation marks."
                )

            ticket = {
                name: (value or "").strip()
                for name, value in row.items()
            }

            # Skip completely empty rows.
            if not any(ticket.values()):
                continue

            if not ticket["issue"]:
                raise ValueError(
                    f"CSV row {row_number} has an empty issue."
                )

            tickets.append(ticket)

    if not tickets:
        raise ValueError("The CSV contains no tickets.")

    return columns, tickets


def main():
    print("=== Step 1: Reading support tickets ===")
    columns, tickets = read_tickets()

    print("Columns:", columns)
    print("Ticket count:", len(tickets))
    print("First ticket:", tickets[0])

    if CHECK_INPUT_ONLY:
        print(
            "\nCSV check passed. "
            "No Gemini requests were made and no results were overwritten."
        )
        return

    # Import only after the input check.
    from scraper import load_corpus
    from retriever import retrieve
    from agent import triage_ticket

    print("\n=== Step 2: Loading support corpus ===")
    corpus = load_corpus()

    if not corpus:
        raise RuntimeError(
            "No support corpus loaded. Fix corpus loading first."
        )

    print("Loaded documentation for:", list(corpus.keys()))

    output_columns = [
        name for name in columns
        if name not in RESULT_FIELDS
        and name not in {"processing_state", "error"}
    ]
    output_columns += RESULT_FIELDS + ["processing_state", "error"]

    print("\n=== Step 3: Triaging tickets ===")
    completed = 0
    failed = 0

    with (
        LOG_FILE.open("w", encoding="utf-8") as log,
        OUTPUT_FILE.open(
            "w", newline="", encoding="utf-8"
        ) as output_file,
    ):
        writer = csv.DictWriter(
            output_file,
            fieldnames=output_columns,
            extrasaction="ignore",
        )
        writer.writeheader()
        log.write("=== SUPPORT TRIAGE AGENT LOG ===\n")

        for number, ticket in enumerate(tickets, start=1):
            issue = ticket["issue"]
            subject = ticket["subject"]
            company = ticket["company"]

            if company.lower() in {"", "none", "nan"}:
                company = None

            print(f"Processing ticket {number}/{len(tickets)}")

            log.write(
                f"\n{'=' * 60}\n"
                f"Ticket #{number}\n"
                f"Company: {company}\n"
                f"Subject: {subject}\n"
                f"Issue: {issue}\n"
            )

            output_row = dict(ticket)
            output_row.update({
                field: "" for field in RESULT_FIELDS
            })
            output_row["processing_state"] = "failed"
            output_row["error"] = ""

            try:
                docs = retrieve(
                    f"{subject} {issue}",
                    company,
                    corpus,
                )

                result = triage_ticket(
                    issue,
                    subject,
                    company,
                    docs,
                    log_file=log,
                )

                for field in RESULT_FIELDS:
                    output_row[field] = result[field]

                output_row["processing_state"] = "completed"
                completed += 1
                print(f"  Decision: {result['status']}")

            except Exception as error:
                error_message = (
                    f"{type(error).__name__}: {error}"
                )
                output_row["error"] = error_message
                failed += 1

                log.write(f"\n[ERROR]\n{error_message}\n")
                print(f"  Failed: {error_message}")

            # Save each ticket immediately, including failures.
            writer.writerow(output_row)
            output_file.flush()
            log.flush()

    print("\n=== Processing finished ===")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Results: {OUTPUT_FILE}")
    print(f"Log: {LOG_FILE}")


if __name__ == "__main__":
    main()