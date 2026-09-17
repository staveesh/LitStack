You are a senior full-stack engineer and product architect. I want you to help me design and implement a personal research-paper management system for an academic researcher.

Do not build a generic PDF summarizer or “chat with your papers” application.

The system should implement a workflow for turning a large literature collection into a structured research knowledge base:

DISCOVER → TRIAGE → READ → EXTRACT → CONNECT → SYNTHESIZE → RESURFACE → WRITE

The key design principle is:

> Papers are source material. Research questions, claims, evidence, and open questions are the actual knowledge structure.

The system should use AI primarily for organization, retrieval, structured extraction, synthesis, and recommendation. It should not treat AI-generated summaries as authoritative.

## 1. Product goal

I am a computer-science researcher who reads large numbers of research papers.

I want a system that helps me:

1. maintain an inbox of potentially relevant papers;
2. decide which papers are worth reading;
3. keep track of WHY I want to read each paper;
4. distinguish skim/read/deep-read/citation-only papers;
5. extract structured information from papers;
6. record my own interpretation separately from AI-generated content;
7. connect papers to research questions and claims;
8. maintain evidence for and against claims;
9. identify gaps and unanswered questions in the literature;
10. synthesize multiple papers into higher-level insights;
11. retrieve papers and evidence when I am writing;
12. periodically resurface important or neglected material.

The system should reduce research bookkeeping rather than simply generate more text.

---

# 2. Core conceptual model

The system should treat the following as first-class entities.

## Paper

A research paper imported from Zotero or manually added.

Fields should include at minimum:

* id
* zotero_key
* title
* authors
* year
* venue
* DOI
* URL
* abstract
* PDF path / attachment reference
* citation key
* date_added
* date_modified
* workflow_status
* relevance_score
* priority
* reading_reason
* created_at
* updated_at

Workflow status should support:

* inbox
* triaged
* skim
* deep_read
* read
* citation_only
* archived

A paper may belong to multiple projects, research questions, claims, and themes.

---

## Project

Represents a research project or manuscript.

Examples:

* Agent Privacy Enforcement
* Broadband Sampling
* Related Work for Paper X

Fields:

* id
* name
* description
* active
* created_at

---

## ResearchQuestion

This is more important than folders/topics.

Example:

“Where should privacy enforcement for LLM agents be placed?”

Fields:

* id
* project_id
* question
* motivation
* status
* notes
* created_at

Status:

* active
* partially_answered
* answered
* abandoned

Papers may map to multiple research questions.

---

## ReadingIntent

Represents WHY I am opening a particular paper.

Example:

“I want to determine whether their runtime monitor is outside the agent's trust boundary and whether the agent can bypass it.”

Fields:

* id
* paper_id
* research_question_id optional
* intent
* created_at
* resolved_at
* resolution_notes

This is important.

The application should encourage creation of a reading intent before a deep read.

---

## PaperExtraction

AI-generated structured extraction from a paper.

Fields:

* paper_id
* problem
* key_idea
* approach
* architecture
* threat_model
* assumptions
* dataset
* evaluation_methodology
* baselines
* metrics
* main_results
* limitations
* future_work
* relevant_sections
* important_figures
* confidence / provenance metadata

Every extracted field should ideally retain provenance pointing to pages or passages in the source paper.

AI-generated extraction MUST be visually distinguished from human-authored notes.

---

## HumanPaperNote

My own interpretation of the paper.

Use fields such as:

* why_i_care
* what_surprised_me
* what_i_dont_believe
* relation_to_my_work
* what_i_might_cite_this_for
* methodological_ideas
* unanswered_questions
* freeform_notes

These fields must never be silently overwritten by AI.

---

## Claim

A proposition I may eventually make in a research paper.

Example:

“Allowing an LLM to rewrite security-sensitive messages introduces failure modes that deterministic deletion avoids.”

Fields:

* id
* project_id
* claim
* status
* confidence
* notes
* created_at
* updated_at

Status:

* hypothesis
* weak_evidence
* supported
* contested
* rejected

---

## Evidence

Connects a paper to a claim.

Fields:

* id
* claim_id
* paper_id
* evidence_type
* evidence_text
* source_location
* strength
* notes

evidence_type:

* supports
* contradicts
* qualifies
* background
* methodological

The system should let one paper provide evidence for many claims.

---

## OpenQuestion

Represents a research gap, uncertainty, or unresolved question.

Example:

“Can a network-side privacy monitor recover sufficient semantic context without access to agent reasoning traces?”

Fields:

* id
* project_id
* question
* origin
* status
* importance
* notes
* created_at

Status:

* open
* investigating
* answered
* converted_to_experiment
* abandoned

A paper may:

* answer an open question;
* partially answer it;
* create a new one.

---

## SynthesisNote

Higher-level knowledge built from multiple papers.

Examples:

* Runtime privacy enforcement architectures
* Agent privacy evaluation methodologies
* Threat models used in agent-security systems

Fields:

* id
* project_id
* title
* body
* synthesis_type
* created_at
* updated_at

A synthesis note should link to multiple papers, claims, and research questions.

---

# 3. Important relationships

The database should naturally support:

Paper ↔ ResearchQuestion

Paper ↔ Claim

Paper ↔ OpenQuestion

Paper ↔ SynthesisNote

Claim ↔ Evidence ↔ Paper

Project → ResearchQuestions

Project → Claims

Project → OpenQuestions

Project → SynthesisNotes

Paper → ReadingIntent

Paper → PaperExtraction

Paper → HumanPaperNote

Do NOT try to force the entire system into a folder hierarchy.

Use a relational or graph-friendly data model.

---

# 4. Zotero integration

Zotero should remain the canonical source for:

* bibliographic metadata
* PDFs
* citation keys
* collections

My application should maintain its own higher-level research metadata.

Implement a Zotero integration layer.

Preferred behavior:

* import Zotero papers;
* periodically sync metadata;
* detect newly added papers;
* preserve Zotero item keys;
* retrieve PDF attachments where possible;
* map Zotero collections to projects optionally;
* never overwrite Zotero metadata without an explicit user action.

The app-specific entities such as:

* research questions
* claims
* evidence
* reading intents
* open questions
* AI extraction

should live in our application's own database.

Design the integration so Zotero is replaceable and not deeply coupled to the domain model.

---

# 5. AI architecture

Create an abstraction such as:

LLMProvider

with support for interchangeable providers.

Initially support:

* Anthropic
* OpenAI
* optionally a local OpenAI-compatible endpoint such as LM Studio

Do not hard-code the entire system to one provider.

All AI operations should use structured outputs validated against schemas.

Use JSON schema / Pydantic / Zod or equivalent.

Persist:

* model name
* prompt version
* timestamp
* source inputs
* generated output
* confidence where appropriate

so AI-generated data is auditable.

---

# 6. AI feature: Inbox triage

The inbox should show newly imported papers.

Allow selecting many papers and running:

“AI Triage”

The AI should receive:

* title
* abstract
* project context
* active research questions
* possibly my existing claims/open questions

It should return for each paper:

* relevance score
* recommended action:

  * deep_read
  * skim
  * citation_only
  * ignore
* reason
* which research questions it relates to
* recommended reading intent
* sections/topics to inspect
* confidence

Example:

Paper: XYZ

Recommendation:
SKIM

Reason:
Relevant to your question about enforcement placement, but its contribution is primarily endpoint-side policy classification.

Read:
Sections 3 and 5.

Reading intent:
Determine whether enforcement occurs inside the agent's trust boundary.

The UI must make AI recommendations editable rather than automatically applying them.

---

# 7. AI feature: Reading contract

Before marking a paper as deep_read, allow:

“Generate Reading Contract”

Given:

* paper
* active project
* research question
* reading intent

generate:

* why this paper is relevant
* 2–4 sections to prioritize
* claims worth verifying manually
* important figures/tables
* assumptions to examine
* comparisons to my own work
* sections that can probably be skipped

The goal is selective reading, not summarization.

---

# 8. AI feature: Structured paper extraction

After reading or uploading a paper, AI should extract:

* problem
* research question
* key idea
* system architecture
* threat model
* assumptions
* methodology
* datasets
* baselines
* metrics
* principal results
* limitations
* future work
* claims made by authors

Where possible, attach page-level or passage-level provenance.

The AI should NOT generate my personal interpretation.

Human notes must remain separate.

---

# 9. AI feature: Claim extraction and linking

Given a paper and existing project claims, AI should suggest:

* existing claims this paper supports;
* existing claims it contradicts;
* claims it qualifies;
* potentially new claims worth creating.

The system should present suggestions for human approval.

Never automatically add evidence to a claim without approval.

Example output:

Existing claim:
“Endpoint-side privacy enforcement can be bypassed if the agent runtime is compromised.”

Suggested relation:
SUPPORTS

Evidence:
“...”

Source:
Section 4.2 / page 7

Confidence:
0.87

---

# 10. AI feature: Open-question extraction

After processing a paper, allow:

“What remains unanswered?”

The AI should consider BOTH:

* the paper;
* existing project knowledge.

It should propose questions such as:

* assumptions the paper does not test;
* missing baselines;
* unclear deployment conditions;
* contradictory results;
* unexamined design spaces;
* external-validity questions;
* questions arising from comparison with other papers.

Allow the user to promote suggestions to OpenQuestion entities.

---

# 11. AI feature: Cross-paper synthesis

This feature is central.

Do NOT merely concatenate paper summaries.

Given a selected set of papers, synthesize along dimensions such as:

* common approaches
* architectural differences
* assumptions
* threat models
* datasets
* evaluation methods
* baselines
* metrics
* findings
* disagreements
* unresolved questions

Support generating comparison matrices.

For example:

| System | Enforcement placement | Agent trusted? | Semantic LLM? | Enforcement mechanism | Stateful? |
| ------ | --------------------- | -------------- | ------------- | --------------------- | --------- |

The user should be able to save the output as a SynthesisNote.

Every substantive statement should link back to relevant papers.

---

# 12. AI feature: Claim ledger

Create a dedicated Claim Ledger view.

For each claim show:

CLAIM

Supporting evidence:

* Paper A
* Paper B

Contradicting evidence:

* Paper C

Qualifying evidence:

* Paper D

Knowledge gaps:
...

Confidence:
...

The AI may suggest whether confidence should change, but the user controls the final state.

This view should make it easy to answer:

“What evidence do I actually have for this sentence I want to write?”

---

# 13. AI feature: Literature gap finder

Given:

* research questions
* claims
* open questions
* selected papers

ask the AI to identify:

* claims supported by only one source;
* claims with contradictory evidence;
* questions lacking evidence;
* methodological gaps;
* missing comparison dimensions;
* areas where many papers make the same untested assumption.

Do NOT present speculative gaps as established facts.

Clearly distinguish:

* directly evidenced gap;
* inferred gap;
* potential research idea.

---

# 14. AI feature: Contextual resurfacing

Implement natural-language retrieval over my research knowledge.

Example queries:

“Which papers did I read that evaluated privacy/utility tradeoffs?”

“Where have I seen deterministic enforcement outside an LLM?”

“What papers had an LLM rewrite baseline?”

“What evidence do I have for the claim that LLM rewriting can introduce new information?”

“I remember a paper using contextual integrity in agent systems. Which one was it?”

Search should combine:

* semantic retrieval
* structured database filters
* claims
* notes
* extracted paper content

The response should prioritize:

1. relevant entities;
2. explanation of why they match;
3. direct links back to the source.

---

# 15. Weekly research review

Implement a dashboard/action that generates a weekly review.

Inputs:

* papers added this week
* papers read
* human notes
* claims modified
* open questions
* reading queue

Output sections:

NEW THIS WEEK

WHAT I READ

WHAT CHANGED IN MY UNDERSTANDING

CLAIMS STRENGTHENED

CLAIMS CHALLENGED

NEW OPEN QUESTIONS

READ NEXT

NEGLECTED PAPERS

STALE DEEP-READ QUEUE

The AI should recommend no more than ~5 papers as “read next” and explain why.

The goal is queue discipline.

---

# 16. Search / retrieval

Implement both:

### Structured search

Examples:

* workflow_status = deep_read
* project = X
* papers supporting Claim Y
* unread papers connected to Question Z
* papers from 2025–2026
* venue = USENIX Security

### Semantic search

Search over:

* title
* abstract
* extracted content
* human notes
* claims
* evidence
* synthesis notes
* open questions

Use embeddings, but do not rely solely on vector search.

Prefer hybrid search:

structured filtering + keyword/full-text + semantic similarity.

---

# 17. PDF processing

The system should ingest PDFs and extract:

* page-aware text
* headings
* paragraphs
* figures/tables references if feasible

Maintain source provenance.

Do not flatten everything into one opaque text blob if avoidable.

Chunk papers structurally where possible:

* abstract
* introduction
* related work
* methodology
* evaluation
* discussion
* conclusion

Chunking should preserve:

* paper ID
* page
* section
* chunk index

---

# 18. UX requirements

The UX should optimize for researchers rather than consumers.

Primary screens:

1. Inbox
2. Reading Queue
3. Paper Detail
4. Projects
5. Research Questions
6. Claim Ledger
7. Open Questions
8. Synthesis Notes
9. Search
10. Weekly Review

Paper detail should visually separate:

AI EXTRACTION

from

MY NOTES

Never blur those boundaries.

The user must always know whether text is:

* source text;
* AI extraction;
* AI inference;
* human-authored interpretation.

---

# 19. Paper detail layout

A good paper detail page might contain:

HEADER

Title
Authors
Venue
Year
Citation key
Workflow status
Projects

WHY AM I READING THIS?

Reading intent

READING CONTRACT

AI-generated reading guide

PAPER EXTRACTION

Problem
Approach
Threat model
Methods
Evaluation
Results
Limitations

MY NOTES

Why I care
What surprised me
What I don't believe
Relation to my work
What I may cite this for

CONNECTIONS

Research questions
Claims
Open questions
Synthesis notes

EVIDENCE

Claims this paper supports/contradicts

SOURCE

PDF
Annotations
Extracted passages

---

# 20. Important product principles

Follow these rigorously.

### Principle 1

Do not build an “AI summaries” database.

Build a research reasoning system.

### Principle 2

Human-authored interpretation must remain distinct from model-generated extraction.

### Principle 3

Every important AI claim should preserve provenance.

### Principle 4

AI outputs are suggestions until accepted.

### Principle 5

Avoid premature automation.

Prefer:

AI proposes → researcher approves

over:

AI silently modifies knowledge base.

### Principle 6

The app should help me discard papers as aggressively as it helps me collect them.

### Principle 7

Research questions and claims are more important than topic folders.

### Principle 8

Optimize for retrieval six months later.

A successful note should answer:

“Why did I care about this paper?”

not merely:

“What was this paper about?”

---

# 21. Recommended technical architecture

Propose the final stack, but my initial preference is:

Frontend:

* Next.js
* TypeScript
* React
* Tailwind
* shadcn/ui

Backend:

* Python
* FastAPI
* Pydantic

Database:

* PostgreSQL

Vector search:

* pgvector

Background jobs:

* lightweight job queue suitable for local/single-user deployment

PDF:

* PyMuPDF or another robust PDF parser

AI:

* provider abstraction supporting Anthropic/OpenAI/OpenAI-compatible local models

Package/deployment:

* Docker Compose

I want this initially as a single-user application running locally.

Avoid unnecessary distributed systems.

---

# 22. Local-first requirements

This is a personal research system.

Prefer:

* local PostgreSQL
* local PDF storage
* local embeddings optionally
* API keys stored locally
* Docker Compose
* easy backup

Design for future cloud deployment, but do not make cloud infrastructure necessary.

---

# 23. Security / privacy

Research PDFs and notes may be unpublished.

Therefore:

* make external LLM use explicit;
* allow selecting which provider handles a request;
* make it possible later to use local models;
* clearly label when document content will leave the machine;
* never upload the whole library unnecessarily;
* send only the minimum relevant context to external APIs.

---

# 24. MVP definition

Do NOT attempt to build every feature at once.

The MVP should include:

1. Zotero import
2. Paper database
3. Inbox
4. workflow status
5. Projects
6. Research Questions
7. Reading Intent
8. Paper Detail
9. PDF text extraction
10. AI triage
11. AI structured extraction
12. Human notes
13. Claims
14. Evidence links
15. Open Questions
16. basic search

After the MVP works, implement:

17. cross-paper synthesis
18. semantic search
19. weekly review
20. contextual resurfacing
21. literature gap analysis

---

# 25. Initial implementation task

Do not start by dumping hundreds of files.

First:

1. restate the product architecture;
2. identify any requirements that conflict;
3. propose a concrete technical architecture;
4. define the complete relational schema;
5. define major API endpoints;
6. define the major frontend routes/components;
7. define AI operations and their structured schemas;
8. define Zotero synchronization behavior;
9. propose an implementation sequence consisting of small independently testable milestones.

Then begin implementation.

Implement one coherent vertical slice first:

Zotero/imported paper
→ Inbox
→ triage
→ reading intent
→ paper detail
→ structured extraction
→ human note
→ connect to Research Question

Do not proceed to fancy RAG agents, autonomous research agents, knowledge graphs, or complex orchestration until this basic workflow works well.

---

# 26. Engineering standards

Use:

* clean separation of domain logic from infrastructure;
* typed schemas;
* database migrations;
* tests for core business logic;
* explicit error handling;
* idempotent Zotero sync;
* reproducible AI prompts;
* structured LLM outputs;
* provenance tracking;
* minimal dependencies;
* readable code.

Avoid:

* giant service classes;
* AI logic scattered across UI components;
* magic prompts embedded in frontend code;
* irreversible AI actions;
* excessive abstractions before they are necessary.

Prompts should be versioned and live in a dedicated prompts module.

---

# 27. Testing

At minimum test:

* Zotero imports are idempotent;
* metadata updates don't destroy application metadata;
* workflow state transitions;
* AI JSON schema validation;
* claim/evidence relationships;
* deletion constraints;
* provenance references;
* search correctness;
* external AI failures;
* malformed PDF extraction;
* papers without PDFs;
* duplicate DOI/citation key cases.

Create realistic test fixtures using fake academic papers rather than depending on live external APIs for all tests.

---

# 28. Seed/demo data

Include sample data demonstrating the intended workflow.

Example research project:

“Privacy Enforcement for LLM Agents”

Research questions:

* Where should privacy enforcement be placed?
* What information is a recipient entitled to receive?
* How should semantic reasoning be separated from enforcement?
* How should privacy/utility tradeoffs be evaluated?

Example claims:

* Security-sensitive mediation should occur outside the untrusted agent.
* LLM rewriting can introduce enforcement errors.
* Deterministic transformations provide stronger guarantees than free-form generation.

Include fake papers and evidence showing:

* supporting evidence;
* contradicting evidence;
* an unanswered question.

This should make the product understandable immediately after installation.

---

# 29. What I care about most

When making design tradeoffs, optimize in this order:

1. retrieval of useful knowledge later;
2. traceability back to sources;
3. low friction while reading;
4. preserving my own thinking;
5. effective triage;
6. interoperability with Zotero;
7. AI sophistication.

Do NOT optimize first for:

* flashy chat interfaces;
* autonomous agents;
* elaborate visual knowledge graphs;
* social features;
* generic note taking;
* replacing Zotero;
* automatically writing literature reviews.

The application succeeds if six months from now I can ask:

“What evidence did I find for X, what papers disagreed, and why did I think this mattered?”

and obtain a reliable answer with citations back to the original papers.

Start by producing the architecture, schema, API design, frontend design, AI schemas, and milestone plan. Then implement the first vertical slice.
