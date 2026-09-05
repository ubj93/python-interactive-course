"""Pilot content, transfer checks, and a real terminal learner walkthrough."""
import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from course.bridges import BRIDGES, bridges_for, has_review_signal
from course.card_ids import LEGACY_CARD_IDS
from course.catalog import load_catalog
from course.cli import App
from course.diagnostic import _summary
from course.lessons import load_lessons, validate_lesson
from course.progress import Progress
from course.runner import run_code_card


class BashBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.lessons = {lesson.id: lesson for part in cls.catalog for lesson in load_lessons(part)}
        cls.cards = {card.id: card for lesson in cls.lessons.values() for card in lesson.cards}

    def test_pilot_uses_only_new_ids_and_preserves_lesson_structure(self):
        new = {"bash-%s-%s" % (bridge["id"], step) for bridge in BRIDGES for step in ("worked", "modify", "check")}
        self.assertEqual({id for id in self.cards if id.startswith("bash-")}, new)
        self.assertFalse(new.intersection(LEGACY_CARD_IDS.values()))
        self.assertTrue(set(LEGACY_CARD_IDS.values()).issubset(self.cards))
        for bridge in BRIDGES:
            lesson = self.lessons[bridge["lesson"]]
            part = next(part for part in self.catalog if part.num == lesson.part_num)
            self.assertEqual(validate_lesson(lesson, part), [])
            self.assertEqual([card.id for card in lesson.cards[:3]], ["bash-%s-%s" % (bridge["id"], step) for step in ("worked", "modify", "check")])
            self.assertEqual([card.kind for card in lesson.cards[:3]], ["teach", "code", "code"])
            self.assertTrue(lesson.exercise_ids)

    def test_worked_examples_execute_and_each_code_check_requires_a_change(self):
        expected = {"return":"Free: 7\n", "defaults":"NODE-a\nlab\n", "process":"3\n",
                    "collections":"5\nblue pen\n", "aliasing":"['draft', 'checked']\n['draft', 'checked']\n['draft', 'checked', 'sent']\n"}
        for bridge in BRIDGES:
            prefix = "bash-" + bridge["id"] + "-"
            with self.subTest(topic=bridge["id"]):
                worked = self.cards[prefix + "worked"]
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    exec(worked.starter, {})
                self.assertEqual(output.getvalue(), expected[bridge["id"]])
                for step in ("modify", "check"):
                    card = self.cards[prefix + step]
                    self.assertGreaterEqual(len(card.checks), 2)
                    self.assertFalse(run_code_card(card, card.starter).ok, card.id)
                    self.assertTrue(run_code_card(card, card.starter + "\n" + card.solution).ok, card.id)

    def test_checks_reject_the_targeted_misconceptions(self):
        wrong = {
            "return-check": 'def transfer_minutes(files, minutes_each):\n    print(files * minutes_each)\n    return files * minutes_each\n',
            "collections-modify": 'def total_units(rows):\n    return len(rows)\n',
            "collections-check": 'def available_labels(rows):\n    return [word for row in rows if row["units"] > 0 for word in row["label"].split()]\n',
            "aliasing-modify": 'def add_label(labels, extra):\n    labels.append(extra)\n    return labels\n',
            "aliasing-check": 'def upper_first(labels):\n    if labels:\n        labels[0] = labels[0].upper()\n    return labels\n',
            "defaults-modify": 'def add_tag(tag, tags=[]):\n    tags.append(tag.upper())\n    return tags\n',
            "defaults-check": 'def with_retry(delays=None, extra=2, cache=[]):\n    cache[:] = [] if delays is None else delays\n    cache.append(extra)\n    return cache\n',
            "process-modify": 'def read_status(runner):\n    return runner(["fake-status"]).stdout.strip()\n',
            "process-check": 'def probe_ok(runner):\n    try:\n        return runner(["fake-probe"]).returncode == 0\n    except Exception:\n        return False\n',
        }
        for suffix, source in wrong.items():
            card = self.cards["bash-" + suffix]
            with self.subTest(card=card.id):
                self.assertFalse(run_code_card(card, card.starter + "\n" + source).ok)

    def test_old_completion_and_reward_records_survive_new_cards(self):
        lesson = self.lessons["3.1"]
        old = {card.id:{"done":True,"correct":True,"tries":1,"custom":"keep"} for card in lesson.cards[3:]}
        rewards = {card_id:True for card_id in old}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            progress = Progress(path)
            progress.data.update(xp=200, cards=copy.deepcopy(old), card_reward_history=rewards.copy(), solved={"3.1":{"xp":30}})
            progress.save()
            progress = Progress(path)
            self.assertEqual(progress.lesson_progress(lesson), (12,15,False))
            self.assertEqual(progress.record_card(lesson.id,"bash-return-modify",True,True),1)
            self.assertEqual(progress.record_card(lesson.id,"bash-return-modify",True,True),0)
            progress = Progress(path)
            self.assertEqual({key:progress.data["cards"][key] for key in old},old)
            self.assertEqual({key:progress.data["card_reward_history"][key] for key in rewards},rewards)
            self.assertEqual(progress.data["solved"],{"3.1":{"xp":30}})
            self.assertEqual(progress.data["xp"],201)

    def test_diagnostic_links_follow_recorded_signals_without_inventing_a_gap(self):
        row = {"id":"3.1","outcome":"passed","confidence":"confident","help_used":False,"mistake_note":""}
        self.assertFalse(has_review_signal(row))
        for change in ({"outcome":"not_passed"},{"confidence":"needs_review"},{"help_used":True},{"mistake_note":"return is not stdout"}):
            self.assertTrue(has_review_signal({**row,**change}))
        self.assertEqual([bridge["id"] for bridge in bridges_for("1.2")],["return"])
        self.assertEqual(bridges_for("1.3"),[])
        self.assertIn("not directly assessed",bridges_for("3.1")[-1]["prerequisites"])
        with tempfile.TemporaryDirectory() as directory:
            app = App.__new__(App)
            app.catalog = self.catalog
            app.lessons = {part.num:load_lessons(part) for part in self.catalog}
            app.progress = Progress(Path(directory)/"progress.json")
            state = app.progress.start_diagnostic()
            app.progress.reflect_diagnostic("3.1","needs_review","printed instead of returned",state["id"])
            with contextlib.redirect_stdout(io.StringIO()) as output:
                _summary(app,app.progress.diagnostic_state())
            self.assertIn("Optional Bash bridge: Return versus print",output.getvalue())
            self.assertIn("course learn 3.2",output.getvalue())
            self.assertIn("process failures are not directly assessed",output.getvalue())

    def test_explicit_cli_card_review_preserves_completed_answers(self):
        lesson=self.lessons["3.1"]
        part=next(part for part in self.catalog if part.num==3)
        with tempfile.TemporaryDirectory() as directory:
            app=App.__new__(App)
            app.progress=Progress(Path(directory)/"progress.json")
            app.progress.data.update(xp=42,cards={card.id:{"done":True,"correct":True,"tries":1} for card in lesson.cards},card_reward_history={card.id:True for card in lesson.cards if card.checkable})
            app.progress.save()
            before=copy.deepcopy(app.progress.data)
            with patch("builtins.input",return_value="q"),contextlib.redirect_stdout(io.StringIO()) as output:
                app.run_lesson(lesson,part,start_card="bash-return-worked")
            self.assertIn("return a value, print a message",output.getvalue())
            self.assertEqual(app.progress.data,before)
            with self.assertRaises(ValueError):
                app.run_lesson(lesson,part,start_card="bash-process-worked")
            self.assertEqual(app.progress.data,before)

    def test_real_cli_walkthrough_repairs_print_then_solves_independent_data_and_resumes(self):
        lesson = self.lessons["3.1"]
        part = next(part for part in self.catalog if part.num==3)
        with tempfile.TemporaryDirectory() as directory:
            app = App.__new__(App)
            app.progress = Progress(Path(directory)/"progress.json")
            # A learner first repeats the stdout mistake, then repairs it. Their
            # independent check uses a differently written valid calculation.
            answers = ["", "def free_slots(capacity, used):", "    print(capacity - used)", "",
                       "def free_slots(capacity, used):", "    return capacity - used", "",
                       "def transfer_minutes(files, minutes_each):", "    total = files * minutes_each", "    return total", "", "q"]
            with patch("builtins.input",side_effect=answers),contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(app.run_lesson(lesson,part),0)
            self.assertIn("It runs and does the job",output.getvalue())
            self.assertIn("Terminal: type the complete corrected function",output.getvalue())
            saved=Progress(app.progress.path)
            self.assertTrue(all(saved.card_state(lesson.id,card.id)["done"] for card in lesson.cards[:3]))
            self.assertFalse(saved.card_state(lesson.id,lesson.cards[3].id)["done"])
            self.assertEqual(saved.data["xp"],1)  # correction earns no replay XP
            app.progress=saved
            with patch("builtins.input",return_value="q"),contextlib.redirect_stdout(io.StringIO()) as resumed:
                app.run_lesson(lesson,part)
            self.assertIn("Resuming at card 4",resumed.getvalue())


if __name__ == "__main__":
    unittest.main()
