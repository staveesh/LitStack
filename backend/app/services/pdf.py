"""PDF text extraction using PyMuPDF. Preserves page and section structure."""
from pathlib import Path
from typing import Optional


SECTION_KEYWORDS = [
    "abstract", "introduction", "related work", "background",
    "methodology", "method", "approach", "system", "design",
    "evaluation", "experiment", "results", "discussion",
    "conclusion", "future work", "references",
]


def _detect_section(text: str) -> Optional[str]:
    lower = text.lower().strip()
    for kw in SECTION_KEYWORDS:
        if lower.startswith(kw) and len(lower) < len(kw) + 30:
            return kw
    return None


def extract_pdf_chunks(pdf_path: str) -> list[dict]:
    """Extract text from PDF, return list of chunks with page/section metadata."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError("PyMuPDF not installed")

    doc = fitz.open(pdf_path)
    chunks = []
    chunk_idx = 0
    current_section = None
    current_page_start = 1
    current_text = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")  # (x0,y0,x1,y1,text,block_no,block_type)
        for block in blocks:
            text = block[4].strip()
            if not text:
                continue

            detected = _detect_section(text)
            if detected and len(text) < 100:
                # Flush current chunk
                if current_text:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "section": current_section,
                        "page_start": current_page_start,
                        "page_end": page_num,
                        "text": "\n".join(current_text),
                    })
                    chunk_idx += 1
                current_section = detected
                current_page_start = page_num
                current_text = []
            else:
                current_text.append(text)

                # Flush if chunk gets large (~2000 words)
                if sum(len(t.split()) for t in current_text) > 2000:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "section": current_section,
                        "page_start": current_page_start,
                        "page_end": page_num,
                        "text": "\n".join(current_text),
                    })
                    chunk_idx += 1
                    current_page_start = page_num
                    current_text = []

    if current_text:
        chunks.append({
            "chunk_index": chunk_idx,
            "section": current_section,
            "page_start": current_page_start,
            "page_end": len(doc),
            "text": "\n".join(current_text),
        })

    doc.close()
    return chunks


def get_full_text(pdf_path: str, max_chars: int = 15000) -> str:
    """Get full text from PDF, truncated for LLM input."""
    try:
        import fitz
    except ImportError:
        raise RuntimeError("PyMuPDF not installed")

    doc = fitz.open(pdf_path)
    parts = []
    for page in doc:
        parts.append(page.get_text())
        if sum(len(p) for p in parts) > max_chars:
            break
    doc.close()
    return "\n".join(parts)[:max_chars]
