"""Stable identity migration uses only temporary progress and in-memory lessons."""
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from course.card_ids import LEGACY_CARD_IDS, LEGACY_LAYOUT, migrate_card_progress
from course.catalog import load_catalog
from course.lessons import Card, load_lessons, parse_lesson, validate_card_ids, validate_lesson
from course.progress import Progress

ROOT = Path(__file__).resolve().parent.parent


class TestCardIds(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "progress.json"
        self.part = load_catalog()[0]
        self.lesson = load_lessons(self.part)[0]
        self.old_key = "1.1:2"
        self.card_id = LEGACY_CARD_IDS[self.old_key]
        self.state = {"done": True, "correct": True, "tries": 1}

    def test_known_layout_migration_preserves_answers_rewards_and_unknown_records(self):
        original = {"xp": 71, "cards": {self.old_key: self.state, "99.1:52": {"note": "unknown"}},
                    "card_reward_history": {self.old_key: True}, "custom": ["preserve"]}
        self.path.write_text(json.dumps(original))
        p = Progress(self.path)
        self.assertEqual(p.card_state("1.1", self.card_id), self.state)
        self.assertTrue(p.data["card_reward_history"][self.card_id])
        self.assertEqual(p.data["cards"][self.old_key], self.state)
        self.assertEqual(p.data["cards"]["99.1:52"], {"note": "unknown"})
        self.assertEqual(p.data["custom"], ["preserve"])
        p.data["cards"][self.card_id]["tries"] = 3
        self.assertEqual(p.data["cards"][self.old_key]["tries"], 1)
        p.save()
        reloaded = Progress(self.path)
        self.assertEqual(reloaded.data, p.data)
        self.assertEqual(reloaded.xp, 71)

    def test_reorder_insert_and_move_preserve_identity_without_new_mastery(self):
        self.path.write_text(json.dumps({"xp": 71, "cards": {self.old_key: self.state}}))
        p = Progress(self.path)
        card = next(c for c in self.lesson.cards if c.id == self.card_id)
        self.lesson.cards.remove(card)
        self.lesson.cards.insert(0, Card(kind="quiz", id="new-inserted-card"))
        self.lesson.cards.append(card)
        self.assertEqual(p.card_state(self.lesson.id, self.lesson.cards[-1].id), self.state)
        self.assertFalse(p.card_state(self.lesson.id, self.lesson.cards[0].id)["done"])
        # A stable identity also survives moving the card to another lesson.
        self.assertEqual(p.card_state("2.1", card.id), self.state)
        self.assertEqual(p.record_card("1.1", "new-inserted-card", True, True), 1)
        self.assertEqual(p.record_card("2.1", card.id, True, True), 0)

    def test_restart_and_reload_do_not_resurrect_legacy_completion_or_repeat_xp(self):
        self.path.write_text(json.dumps({"xp": 71, "cards": {self.old_key: self.state}}))
        p = Progress(self.path)
        p.restart_lesson(self.lesson)
        p = Progress(self.path)
        self.assertFalse(p.card_state("1.1", self.card_id)["done"])
        self.assertEqual(p.data["cards"][self.old_key], self.state)
        self.assertEqual(p.record_card("1.1", self.card_id, True, True), 0)
        self.assertEqual(p.xp, 71)

    def test_conflicts_prefer_stable_state_and_recovery_is_idempotent(self):
        stable = {"done": False, "correct": False, "tries": 1}
        data = {"cards": {self.old_key: self.state, self.card_id: stable},
                "card_reward_history": {self.old_key: True, self.card_id: False}, "xp": 71}
        migrate_card_progress(data)
        self.assertEqual(data["cards"][self.card_id], stable)
        self.assertFalse(data["card_reward_history"][self.card_id])
        self.assertEqual(data["cards"][self.old_key], self.state)
        before = copy.deepcopy(data)
        migrate_card_progress(data)
        self.assertEqual(data, before)

    def test_legacy_assessment_survives_conflicting_blank_stable_state(self):
        stable = {"done": False, "correct": None, "tries": 0}
        self.path.write_text(json.dumps({"cards": {self.old_key: self.state, self.card_id: stable}, "xp": 71}))
        p = Progress(self.path)
        self.assertEqual(p.card_state("1.1", self.card_id), stable)
        self.assertTrue(p.data["card_reward_history"][self.card_id])
        self.assertEqual(p.record_card("1.1", self.card_id, True, True), 0)
        self.assertEqual(p.xp, 71)

    def test_parser_and_validation_require_unique_authored_ids(self):
        self.assertEqual(len(set(LEGACY_CARD_IDS.values())), len(LEGACY_CARD_IDS))
        self.assertEqual(LEGACY_LAYOUT["source_commit"], "bbf9ada60c1d091672095a6b0caa6c3eec0b6dde")
        path = Path(self.temp.name) / "lesson.md"
        path.write_text(self.lesson.path.read_text())
        parsed = parse_lesson(path, 1, 1, "copy")
        self.assertEqual([c.id for c in parsed.cards], [c.id for c in self.lesson.cards])
        parsed.cards[1].id = parsed.cards[0].id
        self.assertTrue(any("duplicates card ID" in p for p in validate_lesson(parsed, self.part)))
        parsed.cards[1].id = ""
        self.assertTrue(any("stable #card-id" in p for p in validate_lesson(parsed, self.part)))
        self.assertTrue(any("Duplicate card ID" in p for p in validate_card_ids([self.lesson, copy.deepcopy(self.lesson)])))

    def test_positional_callers_cannot_create_new_active_records(self):
        p = Progress(self.path)
        with self.assertRaises(ValueError):
            p.record_card("1.1", 2, True, True)
        with self.assertRaises(ValueError):
            p.card_state("1.1", "1.1:2")


@unittest.skipUnless(shutil.which("node"), "browser migration checks require Node.js")
class TestBrowserCardIds(unittest.TestCase):
    def test_shipped_browser_migrates_reordered_cards_drafts_conflicts_and_imports(self):
        old_key = "1.1:2"
        data = {"xp": 71, "cards": {old_key: {"done": True, "correct": True, "tries": 1}},
                "card_reward_history": {old_key: True}}
        migrate_card_progress(data)
        result = subprocess.run([shutil.which("node"), str(ROOT / "tests" / "web_card_ids.js")],
                                input=json.dumps(data), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        returned = json.loads(result.stdout)
        before = copy.deepcopy(returned)
        migrate_card_progress(returned)
        self.assertEqual(returned, before)
        self.assertEqual(returned["cards"][LEGACY_CARD_IDS[old_key]]["correct"], True)
