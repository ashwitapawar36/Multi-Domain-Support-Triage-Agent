import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "support_tickets" / "support_tickets.csv"
OUTPUT_FILE = ROOT / "support_tickets" / "output_full.csv"
LOG_FILE = ROOT / "triage_full.log"

RESULT_FIELDS = [
    "status",
    "product_area",
    "response",
    "justification",
    "request_type",
]


def read_tickets():
    with INPUT_FILE.open(
        newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV has no header.")

        columns = [name.strip().lower() for name in reader.fieldnames]

        if len(columns) != len(set(columns)):
            raise ValueError("Duplicate CSV column names.")

        missing = {"issue", "subject", "company"} - set(columns)
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")

        reserved = set(RESULT_FIELDS) | {"processing_state", "error"}
        if reserved.intersection(columns):
            raise ValueError("Input CSV contains reserved output columns.")

        reader.fieldnames = columns
        tickets = []

        for number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"CSV row {number} has extra values.")

            ticket = {
                name: (value or "").strip()
                for name, value in row.items()
            }

            if not any(ticket.values()):
                continue

            if not ticket["issue"]:
                raise ValueError(f"CSV row {number} has no issue.")

            tickets.append(ticket)

    if not tickets:
        raise ValueError("CSV contains no tickets.")

    return columns, tickets


def load_progress(columns, tickets):
    rows = []

    for ticket in tickets:
        row = dict(ticket)
        row.update({field: "" for field in RESULT_FIELDS})
        row.update(processing_state="pending", error="")
        rows.append(row)

    if not OUTPUT_FILE.exists():
        return rows

    with OUTPUT_FILE.open(
        newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)
        required = set(columns + RESULT_FIELDS + [
            "processing_state", "error"
        ])

        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Existing output has incompatible columns.")

        saved = list(reader)

    if len(saved) > len(tickets):
        raise ValueError("Existing output has more rows than the input.")

    for index, old in enumerate(saved):
        # Never reuse results against changed or reordered tickets.
        if any(
            old.get(name, "") != tickets[index][name]
            for name in columns
        ):
            raise ValueError(
                f"Input differs from saved output at ticket {index + 1}. "
                "Use a different output filename for changed input."
            )

        state = old.get("processing_state")
        if state not in {"pending", "completed", "failed"}:
            raise ValueError(f"Invalid saved state at ticket {index + 1}.")

        if state == "completed":
            if any(not old.get(field, "").strip() for field in RESULT_FIELDS):
                raise ValueError(
                    f"Incomplete saved result at ticket {index + 1}."
                )

        rows[index].update({
            field: old.get(field, "")
            for field in RESULT_FIELDS + ["processing_state", "error"]
        })

    return rows


def save_progress(rows, columns):
    fields = columns + RESULT_FIELDS + ["processing_state", "error"]
    temporary = OUTPUT_FILE.with_suffix(".csv.tmp")

    with temporary.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        file.flush()
        os.fsync(file.fileno())

    # Replace only after the complete checkpoint has been written.
    os.replace(temporary, OUTPUT_FILE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-input", action="store_true")
    parser.add_argument(
        "--tickets",
        help="Reprocess specific ticket numbers, e.g. 4,12,20",
    )
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()

    if args.tickets is not None and args.retry_failed:
        parser.error("Use either --tickets or --retry-failed.")

    columns, tickets = read_tickets()
    print(f"Loaded {len(tickets)} tickets.")

    if args.check_input:
        print("Columns:", columns)
        print("First ticket:", tickets[0])
        return

    rows = load_progress(columns, tickets)

    if args.tickets is not None:
        try:
            numbers = sorted({
                int(value.strip()) for value in args.tickets.split(",")
            })
        except ValueError:
            parser.error("--tickets must contain comma-separated integers.")

        if any(number < 1 or number > len(tickets) for number in numbers):
            parser.error(f"Ticket numbers must be 1–{len(tickets)}.")

        selected = [number - 1 for number in numbers]

    elif args.retry_failed:
        selected = [
            index for index, row in enumerate(rows)
            if row["processing_state"] == "failed"
        ]

    else:
        # Default: resume unfinished work.
        selected = [
            index for index, row in enumerate(rows)
            if row["processing_state"] != "completed"
        ]

    if not selected:
        print("Nothing to process. No Gemini requests made.")
        return

    from scraper import load_corpus
    from retriever import retrieve
    from agent import triage_ticket

    corpus = load_corpus()
    if not corpus:
        raise RuntimeError("No documentation loaded.")

    # Preserve the previous output before any reprocessing.
    if OUTPUT_FILE.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = OUTPUT_FILE.with_name(
            f"{OUTPUT_FILE.stem}.backup-{stamp}.csv"
        )
        backup.write_bytes(OUTPUT_FILE.read_bytes())
        print(f"Previous results backed up to: {backup.name}")

    print("Selected tickets:", [index + 1 for index in selected])

    with LOG_FILE.open("a", encoding="utf-8") as log:
        log.write(
            f"\n=== RUN {datetime.now(timezone.utc).isoformat()} ===\n"
        )

        for index in selected:
            ticket = tickets[index]
            company = ticket["company"]

            if company.lower() in {"", "none", "nan"}:
                company = None

            print(f"\nProcessing ticket {index + 1}/{len(tickets)}")
            log.write(f"\nTicket #{index + 1}\n")

            row = dict(ticket)
            row.update({field: "" for field in RESULT_FIELDS})
            row.update(processing_state="failed", error="")

            try:
                docs = retrieve(
                    ticket["subject"] + " " + ticket["issue"],
                    company,
                    corpus,
                )
                result = triage_ticket(
                    ticket["issue"],
                    ticket["subject"],
                    company,
                    docs,
                    log_file=log,
                )

                for field in RESULT_FIELDS:
                    row[field] = result[field]

                row["processing_state"] = "completed"
                print("Decision:", result["status"])

            except Exception as error:
                row["error"] = f"{type(error).__name__}: {error}"
                log.write(f"\n[ERROR] {row['error']}\n")
                print("Failed:", row["error"])

            rows[index] = row
            save_progress(rows, columns)
            log.flush()

    print("\nSaved results:")
    for state in ["completed", "failed", "pending"]:
        count = sum(row["processing_state"] == state for row in rows)
        print(f"{state}: {count}")

    print("CSV:", OUTPUT_FILE)
    print("Log:", LOG_FILE)


if __name__ == "__main__":
    main()