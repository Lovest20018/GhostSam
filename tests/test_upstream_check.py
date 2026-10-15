"""Keep the upstream report read-only and flag changes that need S23 review."""

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check-upstream.py"
SPEC = importlib.util.spec_from_file_location("check_upstream", SCRIPT)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)
UPSTREAM_URL = "https://github.com/snothin/GhostSam.git"


class UpstreamCheckTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run_git("init", "-b", "main")
        self.run_git("remote", "add", "upstream", UPSTREAM_URL)
        self.write("README.md", "baseline\n")
        self.commit()
        self.baseline = self.run_git("rev-parse", "HEAD")
        self.run_git("update-ref", "refs/remotes/upstream/main", self.baseline)
        self.config = {
            "ghostsam": {
                "upstream_url": UPSTREAM_URL,
                "default_branch": "main",
                "baseline": self.baseline,
                "tracking_ref": "refs/remotes/upstream/main",
            },
            "review_prefixes": ["app/"],
            "kernelsu": {"revision": "pinned"},
        }

    def run_git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
        ).stdout.strip()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self):
        self.run_git("add", "--all")
        self.run_git(
            "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
            "commit", "-m", "test",
        )

    def advance_upstream(self, path):
        self.write(path, "upstream change\n")
        self.commit()
        self.run_git("update-ref", "refs/remotes/upstream/main", self.run_git("rev-parse", "HEAD"))
        self.run_git("checkout", "--detach", self.baseline)

    def test_identical_upstream_has_no_incoming_changes(self):
        result = checker.report(self.root, self.config)
        self.assertEqual(result["incoming_commits"], [])
        self.assertEqual(result["review_paths"], [])

    def test_protected_path_requires_review(self):
        self.advance_upstream("app/home.kt")
        result = checker.report(self.root, self.config)
        self.assertEqual(result["review_paths"], ["app/home.kt"])

    def test_documentation_change_is_reported_without_marking_it_protected(self):
        self.advance_upstream("docs/new.md")
        result = checker.report(self.root, self.config)
        self.assertEqual(result["incoming_paths"], ["docs/new.md"])
        self.assertEqual(result["review_paths"], [])

    def test_overlap_with_a_custom_commit_requires_review_outside_protected_paths(self):
        self.advance_upstream("docs/shared.md")
        self.write("docs/shared.md", "S23 customization\n")
        self.commit()
        result = checker.report(self.root, self.config)
        self.assertEqual(result["review_paths"], ["docs/shared.md"])

    def test_uncommitted_work_and_head_are_preserved(self):
        self.write("README.md", "unsaved customization\n")
        before = (self.root / "README.md").read_bytes()
        head = self.run_git("rev-parse", "HEAD")
        result = checker.report(self.root, self.config)
        self.assertTrue(result["working_tree_changes"])
        self.assertEqual((self.root / "README.md").read_bytes(), before)
        self.assertEqual(self.run_git("rev-parse", "HEAD"), head)

    def test_unexpected_remote_is_rejected(self):
        self.run_git("remote", "set-url", "upstream", "https://example.invalid/other.git")
        with self.assertRaisesRegex(RuntimeError, "Unexpected upstream URL"):
            checker.report(self.root, self.config, fetch=True)


if __name__ == "__main__":
    unittest.main()
