"""Explicit semantic mappings; ambiguous course strings remain Other."""
import json
import re
from ml.config import ROOT

FACULTIES = json.loads((ROOT / "config/faculty_groups.json").read_text())["groups"]

# Department names are literal meanings; abbreviation hints come from the build spec.
# No fuzzy matching: unseen/uncertain labels get an auditable low-confidence fallback.
COURSES = {
    "Engineering and computing": ["engineering", "koe", "kict", "it",
                                  "computer science", "information technology"],
    "Natural and applied sciences": ["mathematics", "mathemathics", "biotechnology", "kos", "science",
                                     "marine science"],
    "Health sciences": ["biomedical science", "radiography", "nursing", "diploma nursing", "kahs",
                        "kom", "kon", "kop", "kod", "medicine", "pharmacy", "dentistry"],
    "Business and economics": ["human resources", "kenms", "banking studies", "business administration",
                               "econs", "economics", "accounting"],
    "Humanities and social sciences": ["irkhs", "kirkhs", "psychology", "communication",
                                       "human sciences", "social sciences", "usuluddin", "fiqh",
                                       "fiqh fatwa", "kulliyyah of islamic revealed knowledge and human sciences"],
    "Law": ["law", "laws", "aikol"],
    "Education": ["education", "islamic education", "pendidikan islam", "diploma tesl", "koed"],
}
LOOKUP = {label: group for group, labels in COURSES.items() for label in labels}


def normalise_course(value):
    return re.sub(r"\s+", " ", value.strip().casefold())


def describe_course(value):
    normalised = normalise_course(value)
    group = LOOKUP.get(normalised, "Other")
    return {"raw_string": value, "normalised_string": normalised, "canonical_group": group,
            "confidence": "high" if normalised in LOOKUP else "low",
            "reason": ("Literal discipline or abbreviation supplied by the build spec; review against source strings."
                       if normalised in LOOKUP else "Unresolved label; conservatively assigned to Other.")}
