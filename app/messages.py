"""Load the shared copy deck and public configuration without request data."""
import json
from ml.config import ROOT


def read_config(name):
    return json.loads((ROOT / "config" / name).read_text())


COPY = read_config("copy.json")
FACULTY_CONFIG = read_config("faculty_groups.json")
SUPPORT = read_config("support_contacts.json")
