"""Fail clearly before attempting to serve an incomplete research build."""
import argparse
from ml.config import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    required = ["models/model.joblib", "models/metadata.json", "app/main.py"]
    required += ["config/copy.json", "config/support_contacts.json", "app/static/index.html"]
    if args.preview:
        required += ["scripts/capture_previews.py", "app/static/fonts/bricolage-latin.woff2",
                     "app/static/fonts/figtree-latin.woff2"]
    missing = [p for p in required if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit("Not ready: " + ", ".join(missing) +
                         ". Generate missing research artifacts with make data/train, and restore app assets/config.")


if __name__ == "__main__":
    main()
