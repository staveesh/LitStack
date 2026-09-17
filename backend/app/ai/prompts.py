"""Versioned prompts. Each prompt is a (version, system, user_template) tuple.
Never put prompts in routers or UI code."""

TRIAGE_VERSION = "triage-v1"

TRIAGE_SYSTEM = """You are a research assistant helping a computer-science researcher triage papers.
Your job is to assess relevance and recommend a reading depth. Be concise and specific.
Never fabricate claims not supported by the abstract. Uncertainty is acceptable."""

def triage_user(title: str, abstract: str, project_name: str, research_questions: list[str]) -> str:
    rqs = "\n".join(f"- {q}" for q in research_questions) if research_questions else "None provided."
    return f"""Paper to triage:
Title: {title}
Abstract: {abstract}

Project: {project_name}
Active research questions:
{rqs}

Assess relevance and recommend: deep_read, skim, citation_only, or ignore.
Provide a relevance_score 0-1, a reason (2-3 sentences), sections to inspect, and a suggested reading intent."""


EXTRACTION_VERSION = "extraction-v1"

EXTRACTION_SYSTEM = """You are a research assistant performing structured extraction from academic papers.
Extract factual information directly from the text. Do not infer or embellish.
If a field is not present in the text, omit it or leave it empty.
Do not generate the researcher's personal interpretation."""

def extraction_user(text_excerpt: str, title: str) -> str:
    return f"""Extract structured information from this paper.

Title: {title}

Paper text (may be truncated):
{text_excerpt[:12000]}

Fill all fields you can identify from the text. Use direct quotes or close paraphrases.
For claims_made, list explicit claims the authors make about their system's properties."""


READING_CONTRACT_VERSION = "reading-contract-v1"

READING_CONTRACT_SYSTEM = """You are a research assistant helping a researcher read a paper efficiently.
Generate a selective reading guide. Do not summarize — identify what to prioritize."""

def reading_contract_user(
    title: str,
    abstract: str,
    intent: str,
    question: str,
    project: str,
) -> str:
    return f"""Paper: {title}
Abstract: {abstract}

Project: {project}
Research question: {question}
Reading intent: {intent}

Generate a reading contract: why relevant, which sections to prioritize (max 4),
which author claims to verify, important figures, assumptions to examine, what to skip."""


CLAIM_SUGGESTION_VERSION = "claim-suggestion-v1"

CLAIM_SUGGESTION_SYSTEM = """You are a research assistant identifying relationships between a paper and existing research claims.
Be conservative: only suggest links with clear textual evidence. Mark confidence honestly."""

def claim_suggestion_user(
    title: str, abstract: str, existing_claims: list[dict],
) -> str:
    claims_text = "\n".join(
        f"- [{c['id']}] {c['claim']}" for c in existing_claims
    ) if existing_claims else "None."
    return f"""Paper: {title}
Abstract: {abstract}

Existing claims:
{claims_text}

For each relevant existing claim, suggest the relationship (supports/contradicts/qualifies/background/methodological),
evidence text, source location, and confidence.
Also suggest any new claims this paper makes that warrant tracking."""


OQ_SUGGESTION_VERSION = "oq-suggestion-v1"

OQ_SUGGESTION_SYSTEM = """You are a research assistant identifying open questions after reading a paper.
Focus on gaps the paper reveals, untested assumptions, missing baselines, and unresolved tensions with other work."""

def oq_suggestion_user(title: str, abstract: str, existing_questions: list[str]) -> str:
    existing = "\n".join(f"- {q}" for q in existing_questions) if existing_questions else "None."
    return f"""Paper: {title}
Abstract: {abstract}

Existing open questions in project:
{existing}

What remains unanswered? Propose new open questions this paper surfaces or fails to address.
Rate importance 1-5 and explain the origin of each question."""
