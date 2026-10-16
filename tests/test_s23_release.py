"""Exercise independent versioning and reject accidental S23 publications."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/s23-release.py"
SPEC = importlib.util.spec_from_file_location("s23_release", SCRIPT)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class S23ReleaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("maintenance/s23-baseline.json", json.dumps({"product": {
            "name": "GhostSam S23", "application_id": "com.snothin.ghostsam.s23",
            "version_file": "app/s23-version.properties", "tag_prefix": "s23-v",
            "latest_published": {"version_code": 63},
        }}))
        self.version("0.3.0-rc.1", "64")
        self.write("docs/releases/s23-v0.3.0-rc.1.zh.md", "S23 release candidate\n")

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def version(self, name, code):
        self.write("app/s23-version.properties", f"versionName={name}\nversionCode={code}\n")

    def test_candidate_metadata_is_independent_of_legacy_version(self):
        self.write("app/version.properties", "versionName=99.0.0\nversionCode=9999\n")
        result = release.metadata(self.root, "s23-v0.3.0-rc.1")
        self.assertEqual(result["version_name"], "0.3.0-rc.1")
        self.assertEqual(result["version_code"], "64")
        self.assertEqual(result["prerelease"], "true")

    def test_metadata_does_not_change_version_file(self):
        before = (self.root / "app/s23-version.properties").read_bytes()
        release.metadata(self.root)
        self.assertEqual((self.root / "app/s23-version.properties").read_bytes(), before)

    def test_mismatched_or_legacy_release_tag_is_rejected(self):
        for tag in ("s23-v0.4.0", "s23-ksu-3.3.1-r3", "v0.3.0-rc.1"):
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, "must match"):
                release.metadata(self.root, tag)

    def test_development_build_cannot_be_published(self):
        self.version("0.3.0-dev", "64")
        self.assertEqual(release.metadata(self.root)["version_name"], "0.3.0-dev")
        with self.assertRaisesRegex(ValueError, "artifacts only"):
            release.metadata(self.root, "s23-v0.3.0-dev")

    def test_release_notes_are_required(self):
        (self.root / "docs/releases/s23-v0.3.0-rc.1.zh.md").unlink()
        with self.assertRaisesRegex(ValueError, "Release notes required"):
            release.metadata(self.root, "s23-v0.3.0-rc.1")

    def test_non_increasing_or_invalid_android_version_is_rejected(self):
        for code in ("63", "1", "-1", "64x", "2100000001"):
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "versionCode"):
                self.version("0.3.0-rc.1", code)
                release.metadata(self.root)

    def test_invalid_version_names_are_rejected(self):
        for name in ("../other", "0.3.0\nbad", "0.3.0-r3", "0.3.0-rc.01"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.version(name, "64")
                release.metadata(self.root)


if __name__ == "__main__":
    unittest.main()
