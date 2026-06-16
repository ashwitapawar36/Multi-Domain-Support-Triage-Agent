import re

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

def score_chunk(chunk, query):
    query_words = set(re.findall(r'\w+', query.lower()))
    chunk_lower = chunk.lower()
    score = sum(1 for w in query_words if w in chunk_lower)
    return score

def retrieve(issue, company, corpus, top_k=3):
    if company and company in corpus:
        sources = {company: corpus[company]}
    else:
        sources = corpus

    best = []
    for src, text in sources.items():
        for chunk in chunk_text(text):
            s = score_chunk(chunk, issue)
            best.append((s, chunk, src))

    best.sort(key=lambda x: x[0], reverse=True)
    top_chunks = best[:top_k]

    if not top_chunks or top_chunks[0][0] == 0:
        return "No relevant documentation found in the support corpus."

    return "\n\n---\n\n".join(f"[{src}]\n{chunk}" for _, chunk, src in top_chunks)