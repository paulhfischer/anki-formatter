from __future__ import annotations

import json
import os
from collections.abc import Callable
from collections.abc import Generator
from contextlib import contextmanager

from anki.notes import Note
from aqt import mw
from aqt.browser import Browser
from aqt.utils import showCritical
from aqt.utils import showInfo

from anki_formatter.formatters import FORMATTERS


def _load_config(directory: str) -> dict[str, dict[str, Callable[[str], tuple[str, bool]]]]:
    config = {}

    for folder_name in os.listdir(directory):
        folder = os.path.join(directory, folder_name)

        if not os.path.isdir(folder):
            continue

        if os.path.basename(folder) in (".git",):
            continue

        with open(os.path.join(folder, "model.json"), encoding="utf-8") as f:
            data = json.load(f)

        config[data["name"]] = {
            field["name"]: FORMATTERS[field.get("formatter", "skip")] for field in data["fields"]
        }

    return config


@contextmanager
def _template_directory() -> Generator[str, None, None]:
    addons_path = mw.addonManager.addonsFolder()
    userfiles_path = os.path.join(addons_path, "user_files")
    templates_path = os.path.join(userfiles_path, "templates")

    os.makedirs(templates_path, exist_ok=True)

    yield templates_path


def _selected_notes(browser: Browser) -> Generator[Note, None, None]:
    for note_id in browser.selectedNotes():
        yield mw.col.getNote(note_id)


def _note_fields(note: Note) -> Generator[str, None, None]:
    for field in note.note_type().get("flds", []):
        yield field["name"]


def _format_note(
    note: Note,
    config: dict[str, dict[str, Callable[[str], tuple[str, bool]]]],
) -> Note | None:
    changed = False

    for field in _note_fields(note):
        formatter = config[note.note_type()["name"]][field]

        original = note[field]
        try:
            formatted_value, did_format = formatter(original)
        except Exception as e:
            showCritical(f"Could not format note {dict(note)}!")
            raise e

        if did_format:
            note[field] = formatted_value
            changed = True

    if changed:
        return note
    else:
        return None


def main(browser: Browser) -> None:
    mw.checkpoint("Format Notes")
    mw.progress.start()

    with _template_directory() as models_dir:
        config = _load_config(models_dir)

    formatted_notes = []
    for note in _selected_notes(browser):
        formatted_note = _format_note(note, config)

        if formatted_note:
            formatted_notes.append(formatted_note)

    mw.col.update_notes(formatted_notes)

    mw.progress.finish()
    mw.reset()

    num_formatted = len(formatted_notes)
    if num_formatted == 1:
        showInfo(f"Updated {num_formatted} note!")
    else:
        showInfo(f"Updated {num_formatted} notes!")
