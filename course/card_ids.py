"""One-time migration from the known shipped positional layout to authored IDs.

The checked-in mapping describes v0.3.4, not the current lesson order. Never
regenerate it after inserting, moving or removing cards. Positional records stay
in the original maps for recovery; only authored keys are used for active work.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

LEGACY_LAYOUT = json.loads(Path(__file__).with_name("legacy_card_ids.json").read_text(encoding="utf-8"))
LEGACY_CARD_IDS = LEGACY_LAYOUT["keys"]
CARD_ID_PATTERN = re.compile(r"[a-z][a-z0-9_-]{2,63}")


def card_key(card_id: str) -> str:
    if not isinstance(card_id, str) or not CARD_ID_PATTERN.fullmatch(card_id):
        raise ValueError("A stable authored card ID is required")
    return card_id


def migrate_card_progress(data: dict) -> dict:
    """Prefer existing authored records; retain legacy and unknown data unchanged."""
    if data.get("card_ids_migrated") == LEGACY_LAYOUT["layout"]:
        return data
    for field in ("cards", "card_reward_history"):
        records = data.get(field)
        if isinstance(records, dict):
            for old_key, card_id in LEGACY_CARD_IDS.items():
                if old_key in records and card_id not in records:
                    records[card_id] = copy.deepcopy(records[old_key])
    # An authored state may deliberately be blank after a restart. Preserve that
    # state while retaining any first-answer opportunity consumed by legacy work.
    cards = data.get("cards")
    if isinstance(cards, dict):
        for old_key, card_id in LEGACY_CARD_IDS.items():
            state = cards.get(old_key)
            if isinstance(state, dict) and (state.get("tries", 0) or state.get("correct") is not None):
                history = data.setdefault("card_reward_history", {})
                if isinstance(history, dict):
                    history.setdefault(card_id, True)
    data["card_ids_migrated"] = LEGACY_LAYOUT["layout"]
    return data
