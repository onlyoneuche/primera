"""Run the complete protocol twice and compare all numerical research tables."""
import hashlib
from pathlib import Path
import subprocess
import sys
from ml.config import OUTPUTS, ROOT


def fingerprints():
    return {str(path.relative_to(OUTPUTS)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in OUTPUTS.glob("*.csv")}


def main():
    for iteration in range(2):
        subprocess.run([sys.executable, "-m", "ml.run_all"], cwd=ROOT, check=True)
        current = fingerprints()
        if not current:
            raise RuntimeError("No numerical tables generated.")
        if iteration == 0:
            first = current
    changed = sorted(key for key in first.keys() | current.keys() if first.get(key) != current.get(key))
    if changed:
        raise SystemExit("Non-deterministic numerical outputs: " + ", ".join(changed))
    print(f"Verified identical contents for {len(first)} CSV outputs across two complete runs.")


if __name__ == "__main__":
    main()
