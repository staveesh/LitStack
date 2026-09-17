"""Core business logic tests. No live external APIs needed."""
import asyncio
try:
    import pytest
except ImportError:
    pytest = None  # type: ignore

# ── Zotero idempotency ─────────────────────────────────────────────────────────

def test_parse_zotero_item_extracts_fields():
    from app.services.zotero import _parse_zotero_item

    item = {
        "key": "ABC123",
        "version": 42,
        "data": {
            "title": "Test Paper",
            "creators": [
                {"creatorType": "author", "lastName": "Smith", "firstName": "John"},
                {"creatorType": "editor", "lastName": "Jones", "firstName": "Alice"},  # should be skipped
            ],
            "date": "2024-03-15",
            "publicationTitle": "Nature",
            "DOI": "10.1234/test",
            "url": "https://example.com",
            "abstractNote": "A test abstract.",
            "citationKey": "smith2024test",
            "dateAdded": "2024-01-01T00:00:00Z",
        },
    }
    result = _parse_zotero_item(item)
    assert result["zotero_key"] == "ABC123"
    assert result["title"] == "Test Paper"
    assert result["authors"] == ["Smith, John"]  # editor excluded
    assert result["year"] == 2024
    assert result["venue"] == "Nature"
    assert result["doi"] == "10.1234/test"
    assert result["zotero_version"] == 42


def test_parse_zotero_item_missing_date():
    from app.services.zotero import _parse_zotero_item
    item = {"key": "X", "version": 1, "data": {"title": "No Date", "creators": [], "date": ""}}
    result = _parse_zotero_item(item)
    assert result["year"] is None


# ── Workflow status transitions ────────────────────────────────────────────────

def test_workflow_status_enum_values():
    from app.models import WorkflowStatus
    assert WorkflowStatus.inbox.value == "inbox"
    assert WorkflowStatus.deep_read.value == "deep_read"
    assert WorkflowStatus.archived.value == "archived"
    # Ensure all expected statuses exist
    expected = {"inbox", "triaged", "skim", "deep_read", "read", "citation_only", "archived"}
    assert {s.value for s in WorkflowStatus} == expected


# ── AI schema validation ───────────────────────────────────────────────────────

def test_triage_result_schema():
    from app.schemas.ai import TriageResult
    result = TriageResult(
        paper_id=1,
        relevance_score=0.85,
        recommended_action="deep_read",
        reason="Directly relevant.",
        suggested_reading_intent="Examine threat model.",
        confidence=0.9,
    )
    assert result.recommended_action == "deep_read"
    assert result.related_question_ids == []
    assert result.sections_to_inspect == []


def test_extraction_result_defaults():
    from app.schemas.ai import ExtractionResult
    result = ExtractionResult(
        problem="p",
        key_idea="k",
        approach="a",
        evaluation_methodology="e",
        main_results="r",
        confidence=0.7,
    )
    assert result.assumptions == []
    assert result.baselines == []
    assert result.limitations == []


# ── PDF chunking ───────────────────────────────────────────────────────────────

def test_section_detection():
    from app.services.pdf import _detect_section
    assert _detect_section("Introduction") == "introduction"
    assert _detect_section("Related Work and Background") == "related work"
    assert _detect_section("This is a normal paragraph with many words.") is None
    assert _detect_section("Evaluation") == "evaluation"


# ── Provenance hashing ─────────────────────────────────────────────────────────

def test_operation_log_hash_is_deterministic():
    import hashlib, json
    input_data = {"paper_id": 42, "project_id": 1}
    h1 = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:16]
    h2 = hashlib.sha256(json.dumps({"project_id": 1, "paper_id": 42}, sort_keys=True).encode()).hexdigest()[:16]
    assert h1 == h2  # sort_keys ensures determinism regardless of dict order


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    # Quick self-check without pytest
    test_parse_zotero_item_extracts_fields()
    test_parse_zotero_item_missing_date()
    test_workflow_status_enum_values()
    test_triage_result_schema()
    test_extraction_result_defaults()
    test_section_detection()
    test_operation_log_hash_is_deterministic()
    print("All checks passed.")
