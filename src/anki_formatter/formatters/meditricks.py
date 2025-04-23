from __future__ import annotations

import sys

from bs4 import BeautifulSoup
from bs4 import Tag

from anki_formatter.formatters.common import fix_encoding
from anki_formatter.formatters.common import replace_symbols

if "pytest" not in sys.modules:  # pragma: no cover
    from aqt.utils import showCritical


def format_meditricks(value: str, minimized: bool = False) -> tuple[str, bool]:
    formatted_value = fix_encoding(value)
    formatted_value = replace_symbols(value, html=False)
    formatted_value = formatted_value.strip()

    if formatted_value == "":
        return formatted_value, value != formatted_value

    soup = BeautifulSoup(formatted_value, "html.parser")

    if len(soup.contents) != 1:  # pragma: no cover
        showCritical(f"Invalid meditricks: {value}")
        return value, False

    element = soup.contents[0]
    if not isinstance(element, Tag):  # pragma: no cover
        showCritical(f"Invalid meditricks: {value}")
        return value, False

    if element.name != "div" or element.attrs["class"] != [
        "mt-anki-iframe-src",
    ]:  # pragma: no cover
        showCritical(f"Invalid meditricks: {value}")
        return value, False

    meditricks_id = element.attrs["data-src"].strip()
    if not meditricks_id or not meditricks_id.isdigit():  # pragma: no cover
        showCritical(f"Invalid meditricks: {value}")
        return value, False

    formatted_value = f'<div class="mt-anki-iframe-src" data-src="{meditricks_id}"></div>'
    return formatted_value, value != formatted_value
