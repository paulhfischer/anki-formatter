from __future__ import annotations

import sys

from anki_formatter.formatters.common import fix_encoding
from anki_formatter.formatters.common import replace_symbols

if "pytest" not in sys.modules:  # pragma: no cover
    from aqt.utils import showCritical


def format_source(value: str) -> tuple[str, bool]:
    formatted_value = fix_encoding(value)
    formatted_value = replace_symbols(formatted_value, html=False)
    formatted_value = formatted_value.strip()

    if formatted_value == "":
        return formatted_value, value != formatted_value

    for source in formatted_value.split(", "):
        if source not in {"AMBOSS", "DocCheck", "Wikipedia", "via medici"}:  # pragma: no cover
            showCritical(f"Unknown source: {source}")

    formatted_value = ", ".join(sorted(value.split(", ")))

    return formatted_value, value != formatted_value
