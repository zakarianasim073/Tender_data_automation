import pandas as pd
from app.models.boq_schema import BOQItem

def parse_boq_excel(path: str):
    df = pd.read_excel(path)
    items = []
    for _, r in df.fillna("").iterrows():
        items.append(BOQItem(
            item_no=str(r.get('item_no', '')),
            description=str(r.get('description', '')),
            unit=str(r.get('unit', 'Nos')),
            quantity=float(r.get('quantity', 0) or 0),
            rate=float(r.get('rate', 0) or 0),
        ))
    return items
