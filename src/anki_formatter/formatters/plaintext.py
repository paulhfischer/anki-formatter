from __future__ import annotations

import warnings

from bs4 import BeautifulSoup

from anki_formatter.formatters.common import fix_encoding
from anki_formatter.formatters.common import replace_symbols


def convert_to_plaintext(value: str) -> tuple[str, bool]:
    value = fix_encoding(value)
    value = replace_symbols(value)
    value = value.strip()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        soup = BeautifulSoup(value, "html.parser")

    formatted_value = soup.get_text().strip()

    return formatted_value, value != formatted_value
