from __future__ import annotations

import json
import os
import subprocess
import tempfile
from collections.abc import Callable
from collections.abc import Generator
from contextlib import contextmanager

from anki.notes import Note
from aqt import mw
from aqt.browser import Browser
from aqt.utils import showInfo

from anki_formatter.formatters import FORMATTERS

REPOSITORY_URL = "https://www.github.com/paulhfischer/anki-templates"


def _load_config(directory: str) -> dict[str, dict[str, Callable[[str], str]]]:
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
def _clone_repository(url: str) -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.check_call(("git", "clone", url, tmpdir))

        yield tmpdir


def _selected_notes(browser: Browser) -> Generator[Note, None, None]:
    for note_id in browser.selectedNotes():
        yield mw.col.getNote(note_id)


def _note_fields(note: Note) -> Generator[str, None, None]:
    for field in note.note_type().get("flds", []):
        yield field["name"]


def _format_note(note: Note, config: dict[str, dict[str, Callable[[str], str]]]) -> Note | None:
    changed = False

    for field in _note_fields(note):
        formatter = config[note.note_type()["name"]][field]

        original = note[field]
        formatted = formatter(original)

        if original != formatted:
            note[field] = formatted
            changed = True

    if changed:
        return note
    else:
        return None


def main(browser: Browser) -> None:
    mw.checkpoint("Format Notes")
    mw.progress.start()

    with _clone_repository(REPOSITORY_URL) as models_dir:
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
