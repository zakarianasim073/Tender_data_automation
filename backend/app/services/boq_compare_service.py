from app.utils.calculations import variance


def compare_boq(boq_a, boq_b):
    b_map = {i.item_no: i for i in boq_b}
    out = []
    mismatch_count = 0
    for a in boq_a:
        b = b_map.get(a.item_no)
        if not b:
            mismatch_count += 1
            out.append({"item_no": a.item_no, "status": "missing_in_b"})
            continue
        status = "match" if abs(a.rate - b.rate) < 0.01 else "rate_diff"
        if status != "match":
            mismatch_count += 1
        out.append({
            "item_no": a.item_no,
            "status": status,
            "rate_a": a.rate,
            "rate_b": b.rate,
            "variance": variance(a.rate, b.rate),
        })

    return {
        "summary": {
            "items_checked": len(boq_a),
            "mismatches": mismatch_count,
            "match_ratio": round((len(boq_a) - mismatch_count) / len(boq_a), 3) if boq_a else 1.0,
        },
        "rows": out,
    }
