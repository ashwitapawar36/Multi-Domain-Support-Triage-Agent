from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMPANY_FOLDERS = {
    "HackerRank": "hackerrank",
    "Claude": "claude",
    "Visa": "visa",
}


def load_corpus():
    corpus = {}

    for company, folder_name in COMPANY_FOLDERS.items():
        folder = ROOT / "data" / folder_name

        if not folder.is_dir():
            raise FileNotFoundError(
                f"Documentation folder not found: {folder}"
            )

        documents = []

        for path in sorted(folder.rglob("*.md")):
            text = path.read_text(encoding="utf-8-sig").strip()

            if text:
                source = path.relative_to(ROOT).as_posix()
                documents.append(
                    f"Source: {source}\n{text}"
                )

        if not documents:
            raise RuntimeError(
                f"No non-empty Markdown documents found for {company}"
            )

        corpus[company] = "\n\n".join(documents)
        print(f"{company}: loaded {len(documents)} documents")

    return corpus