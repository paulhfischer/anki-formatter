from __future__ import annotations

from anki_formatter.formatters.clear import clear
from anki_formatter.formatters.html import format_html
from anki_formatter.formatters.plaintext import convert_to_plaintext
from anki_formatter.formatters.skip import skip

FORMATTERS = {
    "clear": clear,
    "plaintext": convert_to_plaintext,
    "html": format_html,
    "skip": skip,
}
