def normalize_rows(rows):
    return [[(c or '').strip() for c in row] for row in rows if any(row)]
