"""
SOR Models
----------
Data structures for Schedule of Rates items (BWDB and LGED).
Each SOR item has:
  - item_code   (e.g. "04-180-00"  or  "2.02.1.1")
  - description
  - unit
  - rates for each zone (A, B, C, D)
  - source      ("BWDB_2023" or "LGED_2023")
"""

from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class SORItem:
    item_code: str
    description: str
    unit: str
    zone_a: float = 0.0
    zone_b: float = 0.0
    zone_c: float = 0.0
    zone_d: float = 0.0
    source: str = ""          # "BWDB_2023" | "LGED_2023"
    chapter: str = ""         # e.g. "04. Preliminary & Misc. Work"
    sl_no: str = ""           # original serial number from PDF

    def get_rate(self, zone: str) -> float:
        """Return rate for a given zone label (A/B/C/D)."""
        z = zone.upper().strip().replace("ZONE", "").replace("-", "").replace(" ", "")
        return {
            "A": self.zone_a,
            "B": self.zone_b,
            "C": self.zone_c,
            "D": self.zone_d,
        }.get(z, 0.0)

    def as_dict(self) -> dict:
        return {
            "item_code":   self.item_code,
            "description": self.description,
            "unit":        self.unit,
            "zone_a":      self.zone_a,
            "zone_b":      self.zone_b,
            "zone_c":      self.zone_c,
            "zone_d":      self.zone_d,
            "source":      self.source,
            "chapter":     self.chapter,
        }


# BWDB zone → district mapping
BWDB_ZONE_DISTRICTS = {
    "A": [
        "Dhaka", "Narayanganj", "Manikganj", "Narshingdi", "Gazipur",
        "Mymensingh", "Munsiganj", "Kishoreganj", "Tangail", "Jamalpur",
        "Sherpur", "Netrakona",
        "Chattogram", "Rangamati", "Khagrachori", "Cox's Bazar", "Bandarban",
    ],
    "B": ["Sylhet", "Sunamganj", "Hobiganj", "Moulvibazar"],
    "C": [
        "Khulna", "Satkhira", "Bagerhat", "Jashore", "Norail",
        "Barishal", "Jhalkathi", "Pirojpur", "Patuakhali", "Barguna", "Bhola",
        "Faridpur", "Rajbari", "Madaripur", "Shariatpur", "Gopalganj",
        "Kushtia", "Chuadanga", "Meherpur", "Magura", "Jhenaidah",
        "Cumilla", "Brahmanbaria", "Chandpur", "Feni", "Noakhali", "Lakshmipur",
        "Rangpur", "Kurigram", "Gaibandha", "Lalmonirhat", "Niphamari",
        "Thakurgaon", "Panchaghar", "Dinajpur",
    ],
    "D": [
        "Rajshahi", "Naogaon", "Nawabganj", "Natore", "Bogura",
        "Jaipurhat", "Sirajganj", "Pabna",
    ],
}

# LGED zone → division mapping
LGED_ZONE_DIVISIONS = {
    "A": ["Dhaka", "Mymensingh"],
    "B": ["Chattogram", "Sylhet"],
    "C": ["Rajshahi", "Rangpur"],
    "D": ["Khulna", "Barishal"],
}


def detect_bwdb_zone(location: str) -> str:
    """Detect BWDB zone from location string (district or division name)."""
    loc = location.lower()
    for zone, districts in BWDB_ZONE_DISTRICTS.items():
        for d in districts:
            if d.lower() in loc:
                return zone
    return "A"   # default to Zone A if not found


def detect_lged_zone(location: str) -> str:
    """Detect LGED zone from location string (division name)."""
    loc = location.lower()
    for zone, divs in LGED_ZONE_DIVISIONS.items():
        for d in divs:
            if d.lower() in loc:
                return zone
    return "B"   # default to Zone B (Chattogram most common for BWDB work)
