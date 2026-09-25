import math
import re
from collections import Counter

STOP_WORDS = set("""
a an the is are was were be been being
i me my we us our you your they them their
it its this that these those to of in on at
for from with by and or but if as do does did
can could would should will have has had
how what when where please immediately
""".split())


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    ]


def build_chunks(corpus, company):
    chunks = []

    # Match company names without depending on capitalization.
    if company:
        selected = {
            name: text
            for name, text in corpus.items()
            if name.casefold() == company.strip().casefold()
        }
    else:
        selected = corpus

    for name, text in selected.items():
        # Split BEFORE chunking so articles never get mixed.
        articles = re.split(r"(?m)^Source: ", text)

        for article in articles:
            if not article.strip():
                continue

            source, separator, body = article.partition("\n")

            if not separator or not body.strip():
                continue

            # Remove Markdown metadata from the searchable body.
            body = re.sub(
                r"\A\s*---\s*\n.*?\n---\s*(?:\n|$)",
                "",
                body,
                count=1,
                flags=re.DOTALL,
            )

            words = body.split()
            chunk_size = 350
            overlap = 70

            for start in range(0, len(words), chunk_size - overlap):
                excerpt = " ".join(words[start:start + chunk_size])
                tokens = tokenize(excerpt)

                if tokens:
                    chunks.append({
                        "company": name,
                        "source": source.strip(),
                        "text": excerpt,
                        "counts": Counter(tokens),
                        "length": len(tokens),
                    })

                if start + chunk_size >= len(words):
                    break

    return chunks


def retrieve(issue, company, corpus, top_k=3):
    query_words = set(tokenize(issue))
    chunks = build_chunks(corpus, company)

    if not query_words or not chunks:
        return "No relevant documentation found in the support corpus."

    total = len(chunks)
    average_length = sum(
        chunk["length"] for chunk in chunks
    ) / total

    document_frequency = Counter()

    for chunk in chunks:
        document_frequency.update(chunk["counts"].keys())

    ranked = []
    k1 = 1.5
    b = 0.75

    for chunk in chunks:
        score = 0.0

        for word in query_words:
            frequency = chunk["counts"].get(word, 0)

            if frequency == 0:
                continue

            matches = document_frequency[word]
            idf = math.log(
                1 + (total - matches + 0.5) / (matches + 0.5)
            )

            denominator = frequency + k1 * (
                1 - b + b * chunk["length"] / average_length
            )

            score += idf * (
                frequency * (k1 + 1) / denominator
            )

        if score > 0:
            ranked.append((score, chunk))

    ranked.sort(key=lambda item: item[0], reverse=True)

    if not ranked:
        return "No relevant documentation found in the support corpus."

    return "\n\n---\n\n".join(
        f"[{chunk['company']}]\n"
        f"Source: {chunk['source']}\n"
        f"{chunk['text']}"
        for score, chunk in ranked[:top_k]
    )