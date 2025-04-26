from __future__ import annotations

import re
import sys

from bs4 import BeautifulSoup
from bs4 import Tag

from anki_formatter.formatters.common import fix_encoding
from anki_formatter.formatters.common import get_website_title
from anki_formatter.formatters.common import replace_symbols

if "pytest" not in sys.modules:  # pragma: no cover
    from aqt.utils import showCritical
    from aqt.utils import showInfo


def format_links(value: str, minimized: bool = False) -> tuple[str, bool]:
    formatted_value = fix_encoding(value)
    formatted_value = replace_symbols(value, html=False)
    formatted_value = formatted_value.strip()

    if formatted_value == "":
        return formatted_value, value != formatted_value

    soup = BeautifulSoup(formatted_value, "html.parser")

    links: list[tuple[str, str]] = []
    for element in soup.contents:
        if not isinstance(element, Tag):
            if isinstance(element, str) and element == "\n":
                continue
            else:  # pragma: no cover
                showCritical(f"Invalid link: {element}")
                return value, False

        if element.name == "br":
            continue

        if element.name != "a" or not element.get("href"):  # pragma: no cover
            showCritical(f"Invalid link: {element}")
            return value, False

        name = element.get_text().strip()  # noqa: F841
        href = element.attrs["href"].strip()
        title = get_website_title(href)

        if "wikipedia.org/wiki" in href:
            regex = r"^(.*) – Wikipedia$"
            page_name = "Wikipedia"
        elif "flexikon.doccheck.com" in href:
            regex = r"^(.*) - DocCheck Flexikon$"
            page_name = "DocCheck Flexikon"
        elif "gelbe-liste.de/wirkstoffe" in href:
            regex = r"^(.*) - Anwendung, Wirkung, Nebenwirkungen \| Gelbe Liste$"
            page_name = "Gelbe Liste"
        elif "gelbe-liste.de/produkte" in href:
            regex = r"^(.*) \| Gelbe Liste$"
            page_name = "Gelbe Liste"
        elif "embryotox.de/arzneimittel" in href:
            regex = r"^Embryotox - (.*)$"
            page_name = "Embryotox"
        else:  # pragma: no cover
            showInfo(f"Unknown website: {href}")

        match = re.match(regex, title)
        if not match:  # pragma: no cover
            showCritical(f"Could not parse website title: {title} ({href})")
            return value, False
        page_title = match.group(1).strip()

        links.append((f"{page_title} – {page_name}", href))

    if minimized:
        formatted_value = "<br>".join(f'<a href="{href}">{name}</a>' for name, href in links)
    else:
        formatted_value = "<br>\n".join(f'<a href="{href}">{name}</a>' for name, href in links)

    return formatted_value, value != formatted_value
