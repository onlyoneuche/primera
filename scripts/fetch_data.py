"""Download only the original Kaggle archive; never overwrite a different CSV."""
import hashlib
import io
import json
from pathlib import Path
import urllib.error
import urllib.request
import zipfile
from ml.config import RAW, ROOT
from ml.validation import validate_bytes

SOURCE = "https://www.kaggle.com/datasets/shariful07/student-mental-health"
DOWNLOAD = "https://www.kaggle.com/api/v1/datasets/download/shariful07/student-mental-health"


def main():
    if RAW.exists():
        raw = RAW.read_bytes()
        try:
            validate_bytes(raw)
        except ValueError as exc:
            raise SystemExit(f"Existing source is invalid: {exc}. It has not been modified; stop and review the source.") from exc
        print("Existing source validated; not modified. SHA-256:", hashlib.sha256(raw).hexdigest())
        return
    try:
        request = urllib.request.Request(DOWNLOAD, headers={"User-Agent": "Primera research dataset setup"})
        with urllib.request.urlopen(request, timeout=60) as response:
            archive = response.read(10_000_001)
        if len(archive) > 10_000_000:
            raise ValueError("Unexpectedly large dataset archive.")
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            csvs = [p for p in z.namelist() if p.lower().endswith(".csv")]
            if len(csvs) != 1:
                raise ValueError("Expected exactly one CSV in the original archive.")
            if z.getinfo(csvs[0]).file_size > 1_000_000:
                raise ValueError("Unexpectedly large survey CSV.")
            raw = z.read(csvs[0])
        validate_bytes(raw)
    except (urllib.error.URLError, zipfile.BadZipFile, ValueError) as exc:
        raise SystemExit(f"Dataset unavailable or invalid: {exc}\n"
                         f"Obtain the original from {SOURCE} and place its unchanged CSV at "
                         "data/raw/Student_Mental_health.csv. No substitute or synthetic data is accepted.") from exc
    RAW.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents overwriting another download or a supplied file.
    with RAW.open("xb") as handle:
        handle.write(raw)
    provenance = {"source": SOURCE, "download": DOWNLOAD,
                  "archive_member": csvs[0], "sha256": hashlib.sha256(raw).hexdigest()}
    (ROOT / "data/source.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print("Downloaded and validated original CSV. SHA-256:", provenance["sha256"])


if __name__ == "__main__":
    main()
