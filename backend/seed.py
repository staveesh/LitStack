"""Seed demo data: Privacy Enforcement for LLM Agents project."""
import asyncio
from app.database import AsyncSessionLocal, engine, Base
from app.models import *
import sqlalchemy


async def seed():
    async with engine.begin() as conn:
        await conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Project
        proj = Project(
            name="Privacy Enforcement for LLM Agents",
            description="Investigating where and how to enforce privacy in LLM-based agent systems.",
        )
        db.add(proj)
        await db.flush()

        # Research questions
        rqs = [
            ResearchQuestion(project_id=proj.id, question="Where should privacy enforcement be placed in an LLM agent architecture?", motivation="Understanding enforcement placement determines the threat model and trust boundaries."),
            ResearchQuestion(project_id=proj.id, question="What information is a message recipient entitled to receive?", motivation="Contextual integrity theory suggests entitlement is context-dependent."),
            ResearchQuestion(project_id=proj.id, question="How should semantic reasoning be separated from enforcement mechanisms?", motivation="Mixing reasoning and enforcement in the same LLM creates audit and bypass problems."),
            ResearchQuestion(project_id=proj.id, question="How should privacy/utility tradeoffs be evaluated in agent systems?", status=RQStatus.partially_answered),
        ]
        for rq in rqs:
            db.add(rq)
        await db.flush()

        # Claims
        claims = [
            Claim(project_id=proj.id, claim="Security-sensitive mediation should occur outside the untrusted agent.", status=ClaimStatus.supported, confidence=0.85),
            Claim(project_id=proj.id, claim="LLM rewriting can introduce enforcement errors by adding or modifying sensitive information.", status=ClaimStatus.weak_evidence, confidence=0.6),
            Claim(project_id=proj.id, claim="Deterministic transformations provide stronger privacy guarantees than free-form LLM generation.", status=ClaimStatus.hypothesis, confidence=0.5),
        ]
        for c in claims:
            db.add(c)
        await db.flush()

        # Open questions
        oqs = [
            OpenQuestion(project_id=proj.id, question="Can a network-side privacy monitor recover sufficient semantic context without access to agent reasoning traces?", importance=5, origin="Emerged from reading enforcement placement papers."),
            OpenQuestion(project_id=proj.id, question="What is the minimum context required for a deterministic privacy filter to make correct decisions?", importance=4, origin="Unanswered by existing work on contextual integrity."),
        ]
        for oq in oqs:
            db.add(oq)
        await db.flush()

        # Fake papers
        papers_data = [
            {
                "title": "OutsideTheLLM: Runtime Privacy Enforcement for LLM Agent Pipelines",
                "authors": ["Chen, Wei", "Patel, Ananya", "Kim, Soo-Jin"],
                "year": 2024,
                "venue": "USENIX Security 2024",
                "abstract": "We propose OutsideTheLLM, a runtime privacy enforcement system that intercepts agent outputs before they reach untrusted channels. Our monitor operates outside the agent trust boundary and applies deterministic redaction rules, avoiding the failure modes of LLM-based rewriting. Evaluation on synthetic benchmarks shows 94% recall on PII removal with a 12ms median latency overhead.",
                "workflow_status": WorkflowStatus.deep_read,
                "reading_reason": "Directly addresses enforcement placement. Claims outside-agent is strictly safer.",
            },
            {
                "title": "ContextualGuard: Privacy-Aware Message Filtering Using Contextual Integrity",
                "authors": ["Moreau, Claire", "Zhang, Yifan"],
                "year": 2024,
                "venue": "CCS 2024",
                "abstract": "ContextualGuard uses contextual integrity theory to determine what information an agent is permitted to relay. We train a classifier to label message flows by context type and apply norms accordingly. The system relies on an LLM to perform norm application, raising questions about adversarial robustness.",
                "workflow_status": WorkflowStatus.read,
                "reading_reason": "Uses CI for entitlement decisions. The LLM-in-the-loop is a concern I want to examine.",
            },
            {
                "title": "AgentPrivacy: Evaluating Privacy Tradeoffs in Autonomous Agent Deployments",
                "authors": ["Park, Jinho", "Ivanova, Maria", "Okonkwo, Chidi"],
                "year": 2023,
                "venue": "IEEE S&P 2023",
                "abstract": "We present a benchmark for evaluating privacy and utility tradeoffs in LLM agent deployments. Our framework measures information loss, task completion rate, and user satisfaction across six redaction strategies. Results show that aggressive redaction significantly reduces task utility even when privacy goals are met.",
                "workflow_status": WorkflowStatus.skim,
                "reading_reason": "Utility/privacy evaluation methodology—relevant to RQ4.",
            },
            {
                "title": "LLMRewrite: When Language Models Fix Their Own Privacy Violations",
                "authors": ["Gupta, Rahul", "Santos, Luisa"],
                "year": 2024,
                "venue": "arXiv 2024",
                "abstract": "We study the use of LLMs to rewrite agent messages to satisfy privacy policies. Through a controlled experiment on 500 messages, we find that LLM rewriting introduces new PII in 8% of cases and fails to remove flagged PII in 14% of cases. We argue that LLM rewriting is an unreliable privacy enforcement mechanism.",
                "workflow_status": WorkflowStatus.inbox,
            },
        ]

        paper_objs = []
        for pd in papers_data:
            p = Paper(**pd)
            db.add(p)
            paper_objs.append(p)
        await db.flush()

        # Link papers to project and research questions via junction tables directly
        # (avoids async lazy-load when using asyncpg engine)
        from app.models import paper_projects, paper_research_questions
        links = [
            (paper_projects, [
                {"paper_id": paper_objs[0].id, "project_id": proj.id},
                {"paper_id": paper_objs[1].id, "project_id": proj.id},
                {"paper_id": paper_objs[2].id, "project_id": proj.id},
                {"paper_id": paper_objs[3].id, "project_id": proj.id},
            ]),
            (paper_research_questions, [
                {"paper_id": paper_objs[0].id, "research_question_id": rqs[0].id},
                {"paper_id": paper_objs[0].id, "research_question_id": rqs[2].id},
                {"paper_id": paper_objs[1].id, "research_question_id": rqs[1].id},
                {"paper_id": paper_objs[2].id, "research_question_id": rqs[3].id},
                {"paper_id": paper_objs[3].id, "research_question_id": rqs[2].id},
            ]),
        ]
        for table, rows in links:
            await db.execute(table.insert(), rows)

        # Evidence
        ev1 = Evidence(
            claim_id=claims[0].id,
            paper_id=paper_objs[0].id,
            evidence_type=EvidenceType.supports,
            evidence_text="OutsideTheLLM demonstrates that an external monitor can enforce privacy with 94% recall and no access to agent internals, confirming outside-agent enforcement is viable.",
            source_location="Section 4, Table 2",
            strength=0.9,
        )
        ev2 = Evidence(
            claim_id=claims[1].id,
            paper_id=paper_objs[3].id,
            evidence_type=EvidenceType.supports,
            evidence_text="LLM rewriting introduces new PII in 8% of cases and fails to remove flagged PII in 14% of cases.",
            source_location="Section 5.2",
            strength=0.85,
        )
        ev3 = Evidence(
            claim_id=claims[0].id,
            paper_id=paper_objs[1].id,
            evidence_type=EvidenceType.qualifies,
            evidence_text="ContextualGuard's norm application still uses an LLM, which the authors acknowledge may be adversarially manipulated. This qualifies the outside-agent claim when the monitor itself uses an LLM.",
            source_location="Section 6",
            strength=0.6,
        )
        for ev in [ev1, ev2, ev3]:
            db.add(ev)

        # Reading intents
        ri1 = ReadingIntent(
            paper_id=paper_objs[0].id,
            research_question_id=rqs[0].id,
            intent="Determine whether their runtime monitor is outside the agent's trust boundary and whether the agent can bypass it by manipulating monitor inputs.",
        )
        ri2 = ReadingIntent(
            paper_id=paper_objs[1].id,
            research_question_id=rqs[1].id,
            intent="Understand how they operationalize contextual integrity norms and whether the LLM-based norm application is bypassable.",
        )
        for ri in [ri1, ri2]:
            db.add(ri)

        # Human notes on the deep-read paper
        note = HumanPaperNote(
            paper_id=paper_objs[0].id,
            why_i_care="This paper directly argues for outside-agent enforcement, which is my core claim. I need to understand both its evidence and its failure modes.",
            what_surprised_me="12ms latency overhead is lower than I expected for a deterministic filter operating on full message payloads.",
            what_i_dont_believe="Their threat model excludes a compromised agent runtime that can craft inputs designed to fool the monitor's redaction rules. This is a significant gap.",
            relation_to_my_work="Supports my claim 1. The deterministic redaction approach aligns with claim 3. But their evaluation uses synthetic PII—I'm skeptical about real-world semantic context.",
            what_i_might_cite_this_for="Evidence that outside-agent enforcement is architecturally viable (latency, recall). Counter-argument: their threat model is weaker than mine.",
            unanswered_questions="What happens when the agent intentionally fragments PII across multiple messages? Does the monitor have sufficient state to detect this?",
        )
        db.add(note)

        await db.commit()
        print(f"Seeded project '{proj.name}' with {len(paper_objs)} papers, {len(rqs)} research questions, {len(claims)} claims.")


if __name__ == "__main__":
    asyncio.run(seed())
