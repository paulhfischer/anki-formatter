from __future__ import annotations

import re

from anki_formatter.formatters.plaintext import convert_to_plaintext


def format_occlusion(value: str, minimized: bool) -> tuple[str, bool]:
    if minimized:  # pragma: no cover
        raise NotImplementedError

    formatted_value, _ = convert_to_plaintext(value, False)

    clozes = [
        (int(match[0]), str(match[1]))
        for match in re.findall(r"\{\{c(\d+)::(.+?)\}\}", formatted_value)
    ]
    clozes = sorted(clozes, key=lambda x: x[0])
    formatted_value = "".join(f"{{{{c{cloze_id}::{image_id}}}}}" for cloze_id, image_id in clozes)

    return formatted_value, value != formatted_value
