import math
import re

from knowledge import (CATEGORIES, PROCESS_STAGES, ESCALATION_LEVELS,
                       FILING_CHECKLIST)

K1 = 1.5          # BM25 term-frequency saturation
B = 0.75          # BM25 length normalisation
MIN_SCORE = 0.3   # ignore very weak matches
DEFAULT_IDS = ["flow-overview", "escalation-overview", "filing-checklist"]

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "of", "to", "in", "on", "and", "or",
    "for", "what", "how", "do", "does", "did", "i", "my", "me", "we", "you", "your",
    "it", "its", "this", "that", "be", "can", "will", "would", "should", "there",
    "with", "as", "at", "by", "from", "about", "usual", "usually", "explain", "tell",
    "please", "give", "show", "why", "when", "which", "who", "if", "so", "not", "no",
    "yes", "then", "than", "have", "has", "had", "been", "process", "processes",
    "more", "take", "takes", "get",
}

# Small synonym map: helps everyday words find the right chunks
SYNONYMS = {
    "pothole": ["road", "damage"], "potholes": ["road", "damage"],
    "garbage": ["waste"], "trash": ["waste"], "dustbin": ["waste"],
    "bin": ["waste"], "bins": ["waste"],
    "streetlight": ["electricity"], "streetlights": ["electricity"],
    "light": ["electricity"], "lights": ["electricity"],
    "power": ["electricity"], "outage": ["electricity"],
    "wire": ["electricity"], "wires": ["electricity"],
    "leak": ["leakage", "water"], "leaks": ["leakage", "water"],
    "pipe": ["water"], "pipes": ["water"], "sewer": ["water"],
    "info": ["information"], "documents": ["information"],
    "document": ["information"], "details": ["information"],
    "required": ["needed"], "need": ["needed"], "needs": ["needed"],
    "appeal": ["escalation"], "ombudsman": ["escalation"],
    "long": ["timeline"], "time": ["timeline"], "days": ["timeline"],
    "delay": ["timeline", "escalation"], "delayed": ["timeline", "escalation"],
    "flow": ["stages"], "steps": ["stages"], "step": ["stages"],
    "toilet": ["sanitation"],
}


# ---------- 1. Chunking ----------

def build_chunks():
    """Turns the knowledge base into small, self-contained chunks."""
    chunks = []
    flow_names = " → ".join(s["title"] for s in PROCESS_STAGES)

    for c in CATEGORIES:
        chunks.append({
            "id": f"{c['id']}-overview", "source": "Categories",
            "title": f"{c['name']}: overview and handling",
            "text": (f"{c['name']} complaints are handled by the {c['department']}. "
                     f"Typical issues: {', '.join(c['sub_issues'])}. "
                     f"They follow the standard resolution flow: {flow_names}."),
        })
        chunks.append({
            "id": f"{c['id']}-info", "source": "Categories",
            "title": f"{c['name']}: information needed to file",
            "text": (f"Information usually needed for a {c['name']} complaint: "
                     f"{'; '.join(c['info_needed'])}."),
        })
        chunks.append({
            "id": f"{c['id']}-timeline", "source": "Categories",
            "title": f"{c['name']}: indicative timeline",
            "text": (f"Indicative timeline for {c['name']}: {c['indicative_timeline']} "
                     f"Actual times vary by case."),
        })

    chunks.append({
        "id": "flow-overview", "source": "Process",
        "title": "Resolution flow overview (7 stages)",
        "text": "The usual resolution flow has 7 stages: " + "; ".join(
            f"{s['step']}. {s['title']}" for s in PROCESS_STAGES) + ".",
    })
    for s in PROCESS_STAGES:
        chunks.append({
            "id": f"stage-{s['step']}", "source": "Process",
            "title": f"Stage {s['step']}: {s['title']}",
            "text": f"{s['description']} (This is part of the resolution flow.)",
        })

    chunks.append({
        "id": "escalation-overview", "source": "Escalation",
        "title": "Escalation ladder overview",
        "text": "Escalation ladder: " + " ".join(
            f"L{e['level']} {e['title']}." for e in ESCALATION_LEVELS)
        + " Move up a level only when the expected timeline has passed without action.",
    })
    for e in ESCALATION_LEVELS:
        chunks.append({
            "id": f"escalation-level-{e['level']}", "source": "Escalation",
            "title": f"Escalation Level {e['level']}: {e['title']}",
            "text": e["when_to_use"],
        })

    chunks.append({
        "id": "filing-checklist", "source": "Checklist",
        "title": "Filing checklist: information needed to file a complaint",
        "text": "Before filing a complaint, prepare: " + "; ".join(FILING_CHECKLIST) + ".",
    })
    chunks.append({
        "id": "scope", "source": "Policy",
        "title": "Scope of this assistant",
        "text": ("This assistant only explains grievance processes. It cannot register, "
                 "file or track complaints and cannot promise outcomes. Citizens should "
                 "use the official grievance portal, app or helpline."),
    })
    return chunks


# ---------- 2. Text processing ----------

def _stem(word):
    """Very light stemming: drop a plural 's', keep the first 5 letters."""
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    return word[:5]


def tokenize(text, expand=False):
    out = []
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if len(w) < 2 or w in STOPWORDS:
            continue
        out.append(_stem(w))
        if expand:
            for extra in SYNONYMS.get(w, []):
                out.append(_stem(extra))
    return out


# ---------- 3. BM25 index (built once) ----------

_CACHE = {}


def _index():
    if "data" not in _CACHE:
        chunks = build_chunks()
        docs = []
        for ch in chunks:
            tokens = tokenize(ch["title"]) * 2 + tokenize(ch["text"])  # title counts double
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            docs.append({"tf": tf, "len": len(tokens)})
        n = len(docs)
        avgdl = sum(d["len"] for d in docs) / n
        df = {}
        for d in docs:
            for t in d["tf"]:
                df[t] = df.get(t, 0) + 1
        idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        _CACHE["data"] = (chunks, docs, idf, avgdl)
    return _CACHE["data"]


def chunk_count():
    return len(_index()[0])


def _search(query, k):
    chunks, docs, idf, avgdl = _index()
    terms = set(tokenize(query, expand=True))
    scored = []
    for ch, d in zip(chunks, docs):
        score = 0.0
        for t in terms:
            tf = d["tf"].get(t)
            if not tf:
                continue
            score += idf[t] * (tf * (K1 + 1)) / (tf + K1 * (1 - B + B * d["len"] / avgdl))
        if score >= MIN_SCORE:
            scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [dict(ch, score=round(s, 2)) for s, ch in scored[:k]]


# ---------- 4. Public functions ----------

def retrieve(query, k=5, context_query=""):
    """Returns the top-k chunks for a question.
    context_query = the previous user question, used for short follow-ups
    like 'explain that more simply'."""
    hits = _search(query, k)
    if not hits and context_query:
        hits = _search(context_query + " " + query, k)
    if not hits:
        chunks = _index()[0]
        hits = [dict(c, score=0.0) for c in chunks if c["id"] in DEFAULT_IDS]
    return hits


def format_context(hits):
    return "\n\n".join(f"[{i + 1}] {h['title']}\n{h['text']}" for i, h in enumerate(hits))