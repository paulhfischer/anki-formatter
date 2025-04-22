from __future__ import annotations

import sys
from contextlib import suppress
from datetime import datetime

from anki_formatter.formatters.common import fix_encoding
from anki_formatter.formatters.common import replace_symbols

if "pytest" not in sys.modules:  # pragma: no cover
    from aqt.utils import showCritical


def format_date(value: str, minimized: bool) -> tuple[str, bool]:
    formatted_value = fix_encoding(value)
    formatted_value = replace_symbols(formatted_value, html=False)
    formatted_value = formatted_value.strip()

    if formatted_value == "":
        return formatted_value, value != formatted_value

    for fmt in {"%d.%m.%Y", "%d/%m/%Y", "%m/%Y", "%d.%m.%y", "%d/%m/%y", "%m/%y"}:
        with suppress(ValueError):
            parsed_date = datetime.strptime(formatted_value, fmt)
            formatted_value = parsed_date.strftime("%m/%Y")
            return formatted_value, value != formatted_value
    else:  # pragma: no cover
        showCritical(f"Unknown date format: {value}")
        return value, False
