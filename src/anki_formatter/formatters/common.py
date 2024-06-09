from __future__ import annotations

import re
from collections.abc import Generator

from bs4 import Comment
from bs4 import NavigableString
from bs4 import Tag


def fix_encoding(text: str) -> str:
    return (
        text.encode("utf-8", errors="ignore")
        .decode("utf-8")
        .replace("\ufeff", "")
        .replace("\u00ad", "")
    )


def replace_symbols(
    text: str,
    *,
    html: bool,
    tags_only: bool = False,
) -> str:
    if not tags_only:
        text = (
            text.replace("&nbsp;", " ")
            .replace("\xa0", " ")
            .replace("“", '"')
            .replace("”", '"')
            .replace("„", '"')
            .replace("‟", '"')
        )

    if not tags_only:
        text = (
            text.replace("&lt;-&gt;", "↔")
            .replace("<->", "↔")
            .replace("-&gt;", "→")
            .replace("->", "→")
            .replace("&lt;-", "←")
            .replace("<-", "←")
            .replace("&lt;=&gt;", "⇔")
            .replace("<=>", "⇔")
            .replace("=&gt;", "⇒")
            .replace("=>", "⇒")
            .replace("&lt;=", "⇐")
            .replace("<=", "⇐")
        )

    if html:
        text = (
            text.replace("⁺", "<sup>+</sup>")
            .replace("⁻", "<sup>-</sup>")
            .replace("⁰", "<sup>0</sup>")
            .replace("¹", "<sup>1</sup>")
            .replace("²", "<sup>2</sup>")
            .replace("³", "<sup>3</sup>")
            .replace("⁴", "<sup>4</sup>")
            .replace("⁵", "<sup>5</sup>")
            .replace("⁶", "<sup>6</sup>")
            .replace("⁷", "<sup>7</sup>")
            .replace("⁸", "<sup>8</sup>")
            .replace("⁹", "<sup>9</sup>")
            .replace("₊", "<sub>+</sub>")
            .replace("₋", "<sub>-</sub>")
            .replace("₀", "<sub>0</sub>")
            .replace("₁", "<sub>1</sub>")
            .replace("₂", "<sub>2</sub>")
            .replace("₃", "<sub>3</sub>")
            .replace("₄", "<sub>4</sub>")
            .replace("₅", "<sub>5</sub>")
            .replace("₆", "<sub>6</sub>")
            .replace("₇", "<sub>7</sub>")
            .replace("₈", "<sub>8</sub>")
            .replace("₉", "<sub>9</sub>")
            .replace("ᵢ", "<sub>i</sub>")
        )
    else:
        text = (
            text.replace("<sup>+</sup>", "⁺")
            .replace("<sup>-</sup>", "⁻")
            .replace("<sup>–</sup>", "⁻")
            .replace("<sup>0</sup>", "⁰")
            .replace("<sup>1</sup>", "¹")
            .replace("<sup>2</sup>", "²")
            .replace("<sup>3</sup>", "³")
            .replace("<sup>4</sup>", "⁴")
            .replace("<sup>5</sup>", "⁵")
            .replace("<sup>6</sup>", "⁶")
            .replace("<sup>7</sup>", "⁷")
            .replace("<sup>8</sup>", "⁸")
            .replace("<sup>9</sup>", "⁹")
            .replace("<sub>+</sub>", "₊")
            .replace("<sub>-</sub>", "₋")
            .replace("<sub>–</sub>", "₋")
            .replace("<sub>0</sub>", "₀")
            .replace("<sub>1</sub>", "₁")
            .replace("<sub>2</sub>", "₂")
            .replace("<sub>3</sub>", "₃")
            .replace("<sub>4</sub>", "₄")
            .replace("<sub>5</sub>", "₅")
            .replace("<sub>6</sub>", "₆")
            .replace("<sub>7</sub>", "₇")
            .replace("<sub>8</sub>", "₈")
            .replace("<sub>9</sub>", "₉")
            .replace("<sub>i</sub>", "ᵢ")
        )

    return text


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
