"""
Structured extraction model for tender PDF parsing.

Every extracted value keeps its source, confidence, and review status.
This allows the cross-check report to show what is complete, duplicated,
conflicting, or waiting for approval.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class FieldEvidence:
    source_file: str
    source_type: str
    page: Optional[int]
    snippet: str
    method: str
    confidence: float


@dataclass
class ExtractedField:
    key: str
    label: str
    value: Any = None
    normalized_value: Any = None
    confidence: float = 0.0
    status: str = "missing"  # matched, conflict, duplicate, missing, review, approved
    evidence: List[FieldEvidence] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def add_evidence(self, evidence: FieldEvidence) -> None:
        self.evidence.append(evidence)
        if evidence.confidence > self.confidence:
            self.confidence = evidence.confidence

    def best_source(self) -> str:
        if not self.evidence:
            return ""
        best = max(self.evidence, key=lambda e: e.confidence)
        page = f" p.{best.page}" if best.page else ""
        return f"{best.source_file}{page}"


@dataclass
class DuplicateFinding:
    field_key: str
    value: Any
    sources: List[str]
    status: str = "duplicate"
    note: str = "Same value found in multiple documents."


@dataclass
class ConflictFinding:
    field_key: str
    values: Dict[str, Any]
    status: str = "conflict"
    note: str = "Different values found for the same field."


@dataclass
class ExtractionBundle:
    fields: Dict[str, ExtractedField] = field(default_factory=dict)
    duplicates: List[DuplicateFinding] = field(default_factory=list)
    conflicts: List[ConflictFinding] = field(default_factory=list)
    raw_text_by_file: Dict[str, str] = field(default_factory=dict)

    def set_field(
        self,
        key: str,
        label: str,
        value: Any,
        source_file: str,
        source_type: str,
        page: Optional[int],
        snippet: str,
        method: str,
        confidence: float,
        normalized_value: Any = None,
    ) -> None:
        field = self.fields.get(key) or ExtractedField(key=key, label=label)
        evidence = FieldEvidence(
            source_file=source_file,
            source_type=source_type,
            page=page,
            snippet=snippet[:500],
            method=method,
            confidence=confidence,
        )

        candidate_norm = normalized_value if normalized_value is not None else value
        if field.value is None:
            field.value = value
            field.normalized_value = candidate_norm
            field.status = "matched" if confidence >= 0.85 else "review"
        else:
            existing = str(field.normalized_value).strip().lower()
            incoming = str(candidate_norm).strip().lower()
            if existing == incoming:
                field.status = "duplicate"
            else:
                field.status = "conflict"
                field.notes.append(f"Conflicting value from {source_file}: {value}")

        field.add_evidence(evidence)
        self.fields[key] = field

    def get(self, key: str, default: Any = "") -> Any:
        field = self.fields.get(key)
        return field.value if field and field.value is not None else default

    def to_dict(self) -> dict:
        return asdict(self)

    def summarize_quality(self) -> Dict[str, int]:
        counts = {"matched": 0, "duplicate": 0, "conflict": 0, "missing": 0, "review": 0, "approved": 0}
        for field in self.fields.values():
            counts[field.status] = counts.get(field.status, 0) + 1
        return counts
