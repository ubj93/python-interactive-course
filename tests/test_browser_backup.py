"""Browser envelope preservation and failure-safe terminal persistence."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from course.backup import backup, restore
from course.browser_backup import FORMAT, MAX_SAFE_INTEGER, pack_progress_document, unpack_progress_document
from course.catalog import find_exercise, load_catalog
from course.progress import Progress
from course.workspace import Workspace

ROOT = Path(__file__).resolve().parent.parent


def browser_document():
    return {
        "format": FORMAT, "version": 1, "exported_at": "2026-09-05T00:00:00.123Z",
        "progress": {
            "version": 1, "xp": 73, "solved": {"1.2": {"xp": 12, "passed_at": "legacy-invalid", "extra": {"keep": 1}}},
            "opened": {"1.2": "invalid timestamp preserved"}, "cards": {"future-card": {"done": True, "correct": None, "tries": 1}},
            "diagnostic_history": [{"future_round": "keep"}], "refresher": {"future_path": "keep"},
            "review_queue": {"future_queue": [1, 2]}, "custom_progress": {"nested": [None, True, "é"]},
        },
        "drafts": {"cpe-course-draft:1.2": "# exercise\n", "cpe-course-draft:card:1.2:3": "# positional code card\n",
                   "cpe-course-draft:card:stable-id": "# stable code card\n", "cpe-course-draft:future/../../opaque": "# never a path\n"},
        "recovery_storage": {"cpe-course-progress-v1": "original raw data", "future-key": None},
        "custom_wrapper": {"retain": [False, 1, {"text": "metadata"}]},
    }


class BrowserDocumentTests(unittest.TestCase):
    def test_unpack_and_pack_preserve_unknown_fields_and_never_alias_inputs(self):
        source = browser_document(); before = copy.deepcopy(source)
        progress, envelope = unpack_progress_document(source)
        progress["xp"] += 5
        packed = pack_progress_document(progress, envelope)
        self.assertEqual(source, before)
        self.assertEqual(packed["progress"]["xp"], 78)
        self.assertEqual({k:v for k,v in packed.items() if k != "progress"}, {k:v for k,v in source.items() if k != "progress"})
        envelope["custom_wrapper"]["retain"].append("changed")
        self.assertEqual(source, before)
        self.assertEqual(pack_progress_document({"xp": 3}), {"xp": 3})

    def test_known_invalid_shapes_and_unsupported_envelopes_are_rejected(self):
        good = browser_document()
        bad_progress = [[], {"xp": True}, {"xp": -1}, {"xp": MAX_SAFE_INTEGER + 1}, {"xp": float("inf")},
                        {"xp": 1, "version": 2}, {"xp": 1, "solved": []}, {"xp": 1, "solved": {"1.2": True}},
                        {"xp": 1, "solved": {"1.2": {"xp": -1}}}, {"xp": 1, "attempts": {"1.2": True}},
                        {"xp": 1, "hints": {"1.2": 0.5}}, {"xp": 1, "cards": {"id": {"tries": -1}}},
                        {"xp": 1, "cards": {"id": {"done": 1}}}, {"xp": 1, "cards": {"id": {"correct": "yes"}}},
                        {"xp": 1, "card_reward_history": {"id": 1}}, {"xp": 1, "daily": {"date": {"done": 1}}},
                        {"xp": 1, "daily": {"date": {"id": 2}}}, {"xp": 1, "days": ["2026-02-30"]},
                        {"xp": 1, "days": ["20260905"]}, {"xp": 1, "peeked": [1]}, {"xp": 1, "last": []},
                        {"xp": 1, "custom": float("nan")}]
        for progress in bad_progress:
            with self.subTest(progress=progress), self.assertRaises(ValueError):
                unpack_progress_document({**good, "progress": progress})
        for value in (None, [], {}, {**good, "version": True}, {**good, "version": 2}, {**good, "format": "other"},
                      {**good, "exported_at": "bad"}, {**good, "drafts": []}, {**good, "drafts": {"cpe-course-draft:": ""}},
                      {**good, "drafts": {"other-key": ""}}, {**good, "drafts": {"cpe-course-draft:1.2": 3}},
                      {"progress": {"xp": 1}}, {"drafts": {}}, {"format": FORMAT}, {"exported_at": good["exported_at"]}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                unpack_progress_document(value, allow_partial_legacy=value != {})
        with self.assertRaises(ValueError):
            unpack_progress_document(json.loads('{"xp":1,"unknown":1e999}'))

    def test_partial_legacy_and_invalid_legacy_timestamps_remain_readable(self):
        progress, wrapper = unpack_progress_document({}, allow_partial_legacy=True)
        self.assertEqual(progress, {}); self.assertIsNone(wrapper)
        for opened in (None, 17, {}, "invalid", "2026-09-05T00:00:00"):
            legacy = {"xp": 71, "opened": {"1.2": opened}, "solved": {"1.3": {"xp": 10}}}
            progress, wrapper = unpack_progress_document(legacy, allow_partial_legacy=True)
            self.assertEqual(pack_progress_document(progress, wrapper), legacy)
            envelope = browser_document(); envelope["progress"] = legacy
            self.assertEqual(unpack_progress_document(envelope)[0], legacy)
        self.assertEqual(unpack_progress_document({"xp": 0, "days": ["0001-01-01", "9999-12-31"]})[0]["xp"], 0)


class TerminalBackupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name); self.path = self.directory / "progress.json"

    def test_real_cli_can_back_up_and_recover_invalid_current_progress(self):
        env = dict(os.environ, COURSE_PROGRESS=str(self.path), COURSE_WORKSPACE=str(self.directory / "workspace"))

        def command(*arguments):
            return subprocess.run([sys.executable, str(ROOT / "course.py"), "--no-color", *arguments],
                                  cwd=self.directory, env=env, capture_output=True, text=True)

        good = self.directory / "valid.zip"
        original = json.dumps(browser_document()).encode()
        with zipfile.ZipFile(good, "w") as zf:
            zf.writestr("manifest.json", json.dumps({"exercises": [], "progress": True}))
            zf.writestr("progress.json", original)
        for index, corrupt in enumerate((b'{"xp":', b'{"format":"future","version":99}')):
            with self.subTest(corrupt=corrupt):
                self.path.write_bytes(corrupt)
                result = command("status")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.path.read_bytes(), corrupt)
                recovery_archive = self.directory / ("corrupt-%s.zip" % index)
                result = command("backup", "--to", str(recovery_archive))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                with zipfile.ZipFile(recovery_archive) as zf:
                    self.assertEqual(zf.read("progress.json"), corrupt)
                result = command("restore", str(good), "--list")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.path.read_bytes(), corrupt)
                recoveries = set(self.directory.glob("progress.json.bak.*"))
                result = command("restore", str(recovery_archive), "--force")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.path.read_bytes(), corrupt)
                self.assertEqual(set(self.directory.glob("progress.json.bak.*")), recoveries)
                result = command("restore", str(good), "--force")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.path.read_bytes(), original)
                created = set(self.directory.glob("progress.json.bak.*")) - recoveries
                self.assertEqual(len(created), 1)
                self.assertEqual(created.pop().read_bytes(), corrupt)
        self.assertFalse((self.directory / "workspace").exists())

    def test_real_cli_write_preserves_browser_drafts_and_envelope_metadata(self):
        original = browser_document()
        original["progress"]["review_queue"] = {"version": 1, "items": {"1.3": {
            "confidence": "confident", "mistake_note": "Keep this existing reflection",
            "next_review": "2026-10-05", "interval_days": 30, "sources": ["exercise"],
        }}, "future_queue": [1, 2]}
        self.path.write_text(json.dumps(original))
        env = dict(os.environ, COURSE_PROGRESS=str(self.path), COURSE_WORKSPACE=str(self.directory / "workspace"))
        command = [sys.executable, str(ROOT / "course.py"), "--no-color", "diagnostic", "reflect", "1.2", "--confidence", "needs-review", "--note", "From the terminal"]
        result = subprocess.run(command, cwd=self.directory, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        exported = json.loads(self.path.read_text())
        progress, envelope = unpack_progress_document(exported)
        self.assertEqual(progress["diagnostic"]["reflections"]["1.2"]["mistake_note"], "From the terminal")
        self.assertEqual(progress["xp"], 73)
        for key in ("drafts", "custom_wrapper", "exported_at", "recovery_storage"):
            self.assertEqual(envelope[key], original[key])
        for key in ("solved", "opened", "diagnostic_history", "refresher", "custom_progress"):
            self.assertEqual(progress[key], original["progress"][key])
        queue = copy.deepcopy(progress["review_queue"])
        reflection = queue["items"].pop("1.2")
        self.assertEqual(reflection["mistake_note"], "From the terminal")
        self.assertEqual(reflection["confidence"], "needs_review")
        self.assertEqual(queue, original["progress"]["review_queue"])
        self.assertFalse((self.directory / "workspace").exists())
        p = Progress(self.path); p.save()
        self.assertEqual(json.loads(self.path.read_text()), exported)

    def test_invalid_load_and_serialization_never_replace_existing_bytes(self):
        for text in ('{"xp":', '{"format":"unknown","version":99}', '{"xp":false}', '{"progress":{"xp":1}}'):
            self.path.write_text(text); before = self.path.read_bytes()
            with self.assertRaises(ValueError):
                Progress(self.path)
            self.assertEqual(self.path.read_bytes(), before)
        self.path.write_text('{"xp":17}')
        p = Progress(self.path); before = self.path.read_bytes(); old = copy.deepcopy(p.data)
        self.path.write_text('{"drafts":{}}')
        with self.assertRaises(ValueError):
            p.load()
        self.assertEqual(p.data, old)
        self.path.write_bytes(before); p.data["unknown"] = object()
        with self.assertRaises(ValueError):
            p.save()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.directory.glob(".progress.json.tmp-*")), [])

    def test_partial_write_and_replace_failures_keep_original_and_clean_temporary(self):
        self.path.write_text(json.dumps(browser_document()))
        p = Progress(self.path); before = self.path.read_bytes(); p.data["xp"] = 74
        real_temporary = tempfile.NamedTemporaryFile
        def failing_temporary(*args, **kwargs):
            stream = real_temporary(*args, **kwargs)
            real_write = stream.write
            def partial(text):
                real_write(text[:13]); stream.flush()
                raise OSError("partial disk write")
            stream.write = partial
            return stream
        with patch("course.progress.tempfile.NamedTemporaryFile", side_effect=failing_temporary), self.assertRaises(OSError):
            p.save()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.directory.glob(".progress.json.tmp-*")), [])
        with patch("course.progress.os.replace", side_effect=OSError("replace denied")), self.assertRaises(OSError):
            p.save()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.directory.glob(".progress.json.tmp-*")), [])
        p.save(); self.assertEqual(json.loads(self.path.read_text())["progress"]["xp"], 74)

    def test_failed_diagnostic_save_rolls_back_memory_and_disk(self):
        self.path.write_text(json.dumps(browser_document()))
        p = Progress(self.path); state = p.start_diagnostic(); before = self.path.read_bytes(); memory = copy.deepcopy(p.data)
        with patch("course.progress.os.replace", side_effect=OSError("replace denied")), self.assertRaises(OSError):
            p.record_diagnostic_attempt("1.2", True, state["id"])
        self.assertEqual(p.data, memory); self.assertEqual(self.path.read_bytes(), before)

    def test_archive_roundtrip_keeps_original_envelope_and_bad_import_is_preflighted(self):
        catalog = load_catalog(); workspace = Workspace(self.directory / "source-workspace")
        source = browser_document(); self.path.write_text(json.dumps(source))
        archive, count, _ = backup(catalog, self.path, self.directory / "copy.zip", workspace=workspace)
        target = self.directory / "restored.json"; restored = Workspace(self.directory / "restored-workspace")
        restore(archive, target, catalog=catalog, workspace=restored)
        self.assertEqual(json.loads(target.read_text()), source)
        ex = find_exercise(catalog, "1.2")
        member = "workspace/answers/" + ex.dir.parent.name + "/" + ex.dir.name + "/exercise.py"
        bad = self.directory / "invalid.zip"
        with zipfile.ZipFile(bad, "w") as zf:
            zf.writestr("manifest.json", json.dumps({"exercises": [member]}))
            zf.writestr(member, "# staged learner answer\n")
            zf.writestr("progress.json", json.dumps({**source, "version": 99}))
        before = target.read_bytes()
        with self.assertRaises(ValueError):
            restore(bad, target, force=True, catalog=catalog, workspace=restored)
        self.assertEqual(target.read_bytes(), before)
        self.assertFalse(restored.answer_path(ex).exists())
        self.assertEqual(list(self.directory.glob("restored.json.bak.*")), [])


if __name__ == "__main__":
    unittest.main()
