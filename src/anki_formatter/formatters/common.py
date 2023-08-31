from __future__ import annotations

import re
from collections.abc import Generator

from bs4 import Comment
from bs4 import NavigableString
from bs4 import Tag


def fix_encoding(text: str) -> str:
    return text.encode("utf-8", errors="ignore").decode("utf-8").replace("\ufeff", "")


def replace_symbols(text: str) -> str:
    return (
        text.replace("&lt;-&gt;", "↔")
        .replace("-&gt;", "→")
        .replace("&lt;-", "←")
        .replace("&lt;=&gt;", "⇔")
        .replace("=&gt;", "⇒")
        .replace("&lt;=", "⇐")
        .replace("&nbsp;", " ")
        .replace("“", '"')
        .replace("”", '"')
        .replace("„", '"')
        .replace("‟", '"')
    )


def strip_whitespace_between_tags(text: str) -> str:
    def __strip(input: re.Match[str]) -> str:
        return input.group().strip()

    return re.sub(r">\s+|\s+<", __strip, text)


def get_child_tags(tag: Tag) -> Generator[Tag, None, None]:
    for child in tag.children:
        if isinstance(child, Tag):
            yield child
        elif isinstance(child, Comment):
            continue
        elif isinstance(child, NavigableString) and child == "\n":
            continue
        else:
            raise ValueError  # pragma: no cover


def get_classes(tag: Tag) -> list[str]:
    tags = tag.get("class")

    if isinstance(tags, list):
        return tags
    else:
        return []


def attrs(attrs: dict[str, str | int | float | None]) -> dict[str, str]:
    return {key: str(value) for key, value in attrs.items() if value is not None}


def format_number(
    number: int | float | str,
    *,
    lower_limit: int | float | None = None,
    upper_limit: int | float | None = None,
) -> int | float:
    number = float(number)
    number = round(number)

    if lower_limit:
        number = max(number, lower_limit)

    if upper_limit:
        number = min(number, upper_limit)

    if number % 1 == 0:
        return int(number)
    else:
        return number
