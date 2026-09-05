"""Run browser transaction regressions and verify its envelope in the terminal."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from course.browser_backup import pack_progress_document, unpack_progress_document


@unittest.skipUnless(shutil.which("node"), "Node is required for browser transaction checks")
class BrowserBackupClientTests(unittest.TestCase):
    def test_browser_transactions_and_cross_client_document(self):
        result = subprocess.run([shutil.which("node"), str(Path(__file__).with_name("web_browser_backup.js"))], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        document = json.loads(result.stdout)
        progress, wrapper = unpack_progress_document(document)
        progress["xp"] += 1
        exported = pack_progress_document(progress, wrapper)
        self.assertEqual(exported["drafts"], document["drafts"])
        self.assertEqual(exported["custom_wrapper"], document["custom_wrapper"])
        self.assertEqual(exported["progress"]["xp"], 45)
