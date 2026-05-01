"""
Rate Checker
------------
Cross-checks BOQ quoted rates against BWDB/LGED SOR rates for a given zone.

Returns:
  - MATCH    : within tolerance
  - MISMATCH : rate differs by more than tolerance
  - MISSING  : item code not found in SOR
  - ABOVE_SOR: quoted rate is HIGHER than SOR (flag for investigation)
  - BELOW_SOR: quoted rate is significantly LOWER than SOR

Generates:
  - Per-item check report
  - Summary statistics
  - Color-coded Excel report
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import pathlib, json


@dataclass
class RateCheckResult:
    item_no:        int
    item_code:      str
    description:    str
    unit:           str
    quantity:       float
    boq_rate:       float       # Rate from submitted BOQ PDF
    quoted_rate:    float       # Contractor quoted rate
    sor_rate:       float       # Rate from SOR for the zone
    sor_source:     str         # "BWDB_2023" | "LGED_2023" | "NOT_FOUND"
    zone:           str         # "A" | "B" | "C" | "D"
    diff_pct:       float       # (quoted - sor) / sor * 100
    status:         str         # MATCH | MISMATCH | MISSING | ABOVE_SOR | BELOW_SOR
    color:          str         # hex color for Excel
    note:           str = ""

    @property
    def boq_amount(self)  -> float: return self.quantity * self.boq_rate
    @property
    def quoted_amount(self) -> float: return self.quantity * self.quoted_rate
    @property
    def sor_amount(self)  -> float: return self.quantity * self.sor_rate


@dataclass
class CheckSummary:
    tender_id:      str
    zone:           str
    total_items:    int
    match_count:    int
    mismatch_count: int
    missing_count:  int
    above_sor_count: int
    below_sor_count: int
    total_boq_amount:    float
    total_quoted_amount: float
    total_sor_amount:    float
    overall_diff_pct:    float
    results:        List[RateCheckResult] = field(default_factory=list)

    @property
    def risk_level(self) -> str:
        if self.mismatch_count + self.above_sor_count >= 5:
            return "HIGH"
        elif self.mismatch_count + self.above_sor_count >= 2:
            return "MEDIUM"
        return "LOW"


# Tolerance for MATCH (±5%)
MATCH_TOLERANCE_PCT = 5.0
# Flag ABOVE_SOR when quoted > SOR by more than this %
ABOVE_SOR_THRESHOLD = 5.0
# Flag BELOW_SOR when quoted < SOR by more than this %
BELOW_SOR_THRESHOLD = 15.0


STATUS_COLORS = {
    "MATCH":     "#92D050",   # green
    "MISMATCH":  "#FFFF00",   # yellow
    "MISSING":   "#D9D9D9",   # grey
    "ABOVE_SOR": "#FF0000",   # red  — quoted rate HIGHER than SOR
    "BELOW_SOR": "#FFC000",   # amber — quoted rate much lower (check for error)
}


def check_rates(
    boq_items: list,
    sor_lookup: dict,      # {item_code: SORItem}
    zone: str,
    tender_id: str,
) -> CheckSummary:
    """
    Cross-check each BOQ item against SOR.
    boq_items: list of BOQItem
    sor_lookup: dict {normalised_code -> SORItem}
    """
    results = []

    for item in boq_items:
        code_key = _normalise_code(item.item_code)
        sor_item = sor_lookup.get(code_key)

        if not sor_item:
            # Try fuzzy match by partial code
            sor_item = _fuzzy_find(code_key, sor_lookup)

        if not sor_item:
            results.append(RateCheckResult(
                item_no=item.item_no,
                item_code=item.item_code,
                description=item.description[:80],
                unit=item.unit,
                quantity=item.quantity,
                boq_rate=item.bwdb_rate,
                quoted_rate=item.quoted_rate,
                sor_rate=0.0,
                sor_source="NOT_FOUND",
                zone=zone,
                diff_pct=0.0,
                status="MISSING",
                color=STATUS_COLORS["MISSING"],
                note="Item code not found in SOR database",
            ))
            continue

        sor_rate = sor_item.get_rate(zone)
        # e-GP BOQ PDFs normally do not include submitted quoted rates.
        # If both BOQ and quoted rates are absent, use the SOR rate as the
        # reference value so totals/checks remain useful instead of all zero.
        boq_rate = item.bwdb_rate if item.bwdb_rate else sor_rate
        quoted = item.quoted_rate if item.quoted_rate else boq_rate
        diff_pct = ((quoted - sor_rate) / sor_rate * 100) if sor_rate else 0.0

        if abs(diff_pct) <= MATCH_TOLERANCE_PCT:
            status = "MATCH"
        elif diff_pct > ABOVE_SOR_THRESHOLD:
            status = "ABOVE_SOR"
        elif diff_pct < -BELOW_SOR_THRESHOLD:
            status = "BELOW_SOR"
        else:
            status = "MISMATCH"

        note = ""
        if status == "ABOVE_SOR":
            note = f"Quoted {diff_pct:+.1f}% ABOVE SOR rate — verify justification"
        elif status == "BELOW_SOR":
            note = f"Quoted {diff_pct:+.1f}% below SOR rate — check for error"
        elif status == "MISMATCH":
            note = f"Quoted {diff_pct:+.1f}% vs SOR"

        results.append(RateCheckResult(
            item_no=item.item_no,
            item_code=item.item_code,
            description=item.description[:80],
            unit=item.unit,
            quantity=item.quantity,
            boq_rate=boq_rate,
            quoted_rate=quoted,
            sor_rate=sor_rate,
            sor_source=sor_item.source,
            zone=zone,
            diff_pct=diff_pct,
            status=status,
            color=STATUS_COLORS[status],
            note=note,
        ))

    # Build summary
    total_boq    = sum(r.boq_amount    for r in results)
    total_quoted = sum(r.quoted_amount for r in results)
    total_sor    = sum(r.sor_amount    for r in results if r.sor_rate > 0)
    overall_diff = ((total_quoted - total_sor) / total_sor * 100) if total_sor else 0

    return CheckSummary(
        tender_id=tender_id,
        zone=zone,
        total_items=len(results),
        match_count=    sum(1 for r in results if r.status == "MATCH"),
        mismatch_count= sum(1 for r in results if r.status == "MISMATCH"),
        missing_count=  sum(1 for r in results if r.status == "MISSING"),
        above_sor_count=sum(1 for r in results if r.status == "ABOVE_SOR"),
        below_sor_count=sum(1 for r in results if r.status == "BELOW_SOR"),
        total_boq_amount=total_boq,
        total_quoted_amount=total_quoted,
        total_sor_amount=total_sor,
        overall_diff_pct=overall_diff,
        results=results,
    )


def _normalise_code(code: str) -> str:
    """Normalise item codes like 4-180, 04-180, and 04-180-00 to one lookup key."""
    raw = str(code or "").strip().lower().replace(" ", "")
    if raw == "mr":
        return "mr"
    parts = [p for p in raw.split("-") if p]
    if not parts:
        return raw
    if parts[0].isdigit():
        parts[0] = parts[0].zfill(2)
    if len(parts) == 2:
        parts.append("00")
    return "-".join(parts)


def _fuzzy_find(code_key: str, sor_lookup: dict):
    """Try relaxed forms: without trailing -00, without dashes, and prefix matching."""
    # Codes like "01", "02", "03" are usually tender row serials, not SOR
    # item codes. Do not fuzzy-match them; that creates false positive rates.
    if "-" not in code_key and len(code_key.replace("-", "")) <= 3:
        return None

    candidates = {code_key, code_key.replace("-", "")}
    parts = code_key.split("-")
    if len(parts) == 3 and parts[2] == "00":
        short = "-".join(parts[:2])
        candidates.add(short)
        candidates.add(short.replace("-", ""))
    for candidate in candidates:
        if candidate in sor_lookup:
            return sor_lookup[candidate]
    prefix = code_key.replace("-", "")[:5]
    for k, v in sor_lookup.items():
        if k.replace("-", "").startswith(prefix):
            return v
    return None


def summary_to_dict(summary: CheckSummary) -> dict:
    return {
        "tender_id":          summary.tender_id,
        "zone":               summary.zone,
        "total_items":        summary.total_items,
        "match":              summary.match_count,
        "mismatch":           summary.mismatch_count,
        "missing":            summary.missing_count,
        "above_sor":          summary.above_sor_count,
        "below_sor":          summary.below_sor_count,
        "risk_level":         summary.risk_level,
        "total_boq_amount":   round(summary.total_boq_amount, 2),
        "total_quoted_amount":round(summary.total_quoted_amount, 2),
        "total_sor_amount":   round(summary.total_sor_amount, 2),
        "overall_diff_pct":   round(summary.overall_diff_pct, 3),
    }
