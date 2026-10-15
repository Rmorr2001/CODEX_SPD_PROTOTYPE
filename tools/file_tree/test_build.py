"""Behavior checks for fresh builds, metadata boundaries, and safe rendering."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from build import GENERATED, build_data, render, source_paths


class FileTreeBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write(self, relative, content="example"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def test_clean_context_reflects_added_and_removed_files(self):
        original = self.write("SPDWEBAPP/HOME/views.py", "def home(request): pass\n")
        first = build_data(self.root)
        self.assertIn("home", first["nodes"]["SPDWEBAPP/HOME/views.py"]["exports"])
        self.write("SPDWEBAPP/HOME/new_feature.py", "class NewFeature: pass\n")
        original.unlink()
        second = build_data(self.root)
        self.assertNotIn("SPDWEBAPP/HOME/views.py", second["nodes"])
        self.assertIn("SPDWEBAPP/HOME/new_feature.py", second["nodes"])
        self.assertNotEqual(first["snapshotId"], second["snapshotId"])

    def test_excludes_private_generated_and_external_symlink_files(self):
        self.write("README.md")
        for name in (".env", ".env.production", "private.key", "media/member.png",
                     "db.sqlite3", "staticfiles/generated.css", ".venv/bin/python", GENERATED):
            self.write(name)
        outside = self.root.parent / (self.root.name + "-outside.py")
        outside.write_text("PRIVATE_CONTENT")
        self.addCleanup(outside.unlink)
        (self.root / "outside.py").symlink_to(outside)
        self.assertEqual(source_paths(self.root), ["README.md"])

    def test_git_mode_uses_tracked_files_but_handles_deleted_working_files(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.write("tracked.py", "pass\n")
        subprocess.run(["git", "add", "tracked.py"], cwd=self.root, check=True)
        self.write("untracked.py", "pass\n")
        self.assertEqual(source_paths(self.root), ["tracked.py"])
        (self.root / "tracked.py").unlink()
        self.assertEqual(source_paths(self.root), [])

    def test_config_files_are_listed_without_reading_their_contents(self):
        self.write("SPDWEBAPP/secret_config.py", "PRIVATE_MARKER")
        self.write("SPDWEBAPP/SPDWEBAPP_CORE/settings.py", "PRIVATE_MARKER")
        original = Path.read_text
        def guarded(path, *args, **kwargs):
            self.assertNotIn(path.name, {"secret_config.py", "settings.py"})
            return original(path, *args, **kwargs)
        with patch.object(Path, "read_text", guarded):
            data = build_data(self.root)
        self.assertEqual(data["fileCount"], 2)
        self.assertNotIn("PRIVATE_MARKER", json.dumps(data))
        self.assertIsNone(data["nodes"]["SPDWEBAPP/secret_config.py"]["lines"])

    def test_commit_links_and_safe_html_payload(self):
        self.write("SPDWEBAPP/HOME/urls.py", "path('</script><script>unsafe</script>', home)\n")
        commit = "a" * 40
        output = self.root / GENERATED
        data = render(self.root, output, commit)
        html = output.read_text()
        self.assertEqual(data["sourceRef"], commit)
        self.assertNotIn("</script><script>unsafe</script>", html)
        self.assertIn("Local route patterns", html)
        self.assertNotIn(GENERATED, build_data(self.root)["nodes"])
        with self.assertRaises(ValueError):
            build_data(self.root, "not-a-commit")


if __name__ == "__main__":
    unittest.main()
