"""Test download validation and file preservation with in-memory HTTP fixtures."""
import hashlib
import io
import json
import contextlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from scripts import fetch_data
from check_foundation import synthetic_csv


def archive_bytes(raw):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zipped:
        zipped.writestr("Student Mental health.csv", raw)
    return buffer.getvalue()


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="primera-download-test-")
        self.root = Path(self.directory.name)
        self.raw = self.root / "data/raw/Student_Mental_health.csv"
        self.root_patch = patch.object(fetch_data, "ROOT", self.root)
        self.raw_patch = patch.object(fetch_data, "RAW", self.raw)
        self.root_patch.start()
        self.raw_patch.start()
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()

    def tearDown(self):
        self.root_patch.stop()
        self.raw_patch.stop()
        self.output.__exit__(None, None, None)
        self.directory.cleanup()

    def test_valid_download_preserves_exact_bytes(self):
        content = synthetic_csv()
        with patch.object(fetch_data.urllib.request, "urlopen", return_value=io.BytesIO(archive_bytes(content))):
            fetch_data.main()
        self.assertEqual(self.raw.read_bytes(), content)
        metadata = json.loads((self.root / "data/source.json").read_text())
        self.assertEqual(metadata["sha256"], hashlib.sha256(content).hexdigest())

    def test_invalid_download_leaves_no_csv(self):
        with patch.object(fetch_data.urllib.request, "urlopen", return_value=io.BytesIO(b"not a zip archive")):
            with self.assertRaises(SystemExit):
                fetch_data.main()
        self.assertFalse(self.raw.exists())

    def test_invalid_dataset_leaves_no_csv(self):
        with patch.object(fetch_data.urllib.request, "urlopen", return_value=io.BytesIO(archive_bytes(b"wrong,data\n"))):
            with self.assertRaises(SystemExit):
                fetch_data.main()
        self.assertFalse(self.raw.exists())

    def test_existing_valid_source_is_not_modified_or_downloaded(self):
        self.raw.parent.mkdir(parents=True)
        content = synthetic_csv()
        self.raw.write_bytes(content)
        original_time = self.raw.stat().st_mtime_ns
        with patch.object(fetch_data.urllib.request, "urlopen") as request:
            fetch_data.main()
            request.assert_not_called()
        self.assertEqual(self.raw.read_bytes(), content)
        self.assertEqual(self.raw.stat().st_mtime_ns, original_time)

    def test_existing_invalid_source_is_never_replaced(self):
        self.raw.parent.mkdir(parents=True)
        self.raw.write_bytes(b"invalid source")
        with patch.object(fetch_data.urllib.request, "urlopen") as request:
            with self.assertRaises(SystemExit):
                fetch_data.main()
            request.assert_not_called()
        self.assertEqual(self.raw.read_bytes(), b"invalid source")


if __name__ == "__main__":
    unittest.main()
