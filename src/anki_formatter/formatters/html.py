from __future__ import annotations

import re
import warnings
from html import escape
from html.parser import HTMLParser as PythonHTMLParser

from bs4 import BeautifulSoup

from anki_formatter.formatters.common import fix_encoding
from anki_formatter.formatters.common import replace_symbols

ALLOWED_TAGS = {"section", "ul", "ol", "li", "b", "sub", "sup", "br", "img", "anki-mathjax"}


def _strip_whitespace_between_tags(text: str) -> str:
    def __strip(input: re.Match[str]) -> str:
        return input.group().strip()

    return re.sub(r">\s+|\s+<", __strip, text)


def preprocess(text: str) -> str:
    text = fix_encoding(text)

    # preserve whitespace after subscript and superscript
    text = text.replace("</sub> ", "</sub>☷").replace("</sup> ", "</sup>☷")

    # preserve whitespace between b-tags
    text = re.sub(r"</b>(?: )+<b>", "</b>☰<b>", text)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        soup = BeautifulSoup(text, "html.parser")

    # remove unwanted tags
    for tag in soup.find_all():
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()

    soup.smooth()
    text = soup.prettify()

    text = _strip_whitespace_between_tags(text)
    text = text.replace("\n", " ")
    text = text.strip()

    return text


def postprocess(text: str) -> str:
    # remove unwanted whitespace between b-tags and merge them
    text = re.sub("</b>(?: )*<b>", "", text)

    # undo preserve whitespace after subscript and superscript
    text = text.replace("</sub>☷", "</sub> ").replace("</sup>☷", "</sup> ")

    # undo preserve whitespace between b-tags
    text = text.replace("</b>☰<b>", "</b> <b>")

    # remove br at end of li-items
    text = re.sub(r"(?:<br>)+</li>", "</li>", text)

    text = text.rstrip()

    return text


class HTMLParser(PythonHTMLParser):
    def __init__(self) -> None:
        super().__init__()

        self.INDENT = 2
        self.ALLOWED_TAGS = ALLOWED_TAGS  # all other tags will be removed
        self.INLINE_TAGS = {
            "b",
            "sub",
            "sup",
            "anki-mathjax",
        }  # these tags will be placed on the current line
        self.NO_BREAK_TAGS = self.INLINE_TAGS | {
            "li",
        }  # inside these tags, there will be no line break

        self.NO_WHITESPACE_BEFORE = {
            ".",
            ",",
            "!",
            "?",
            ":",
            "}}",
            "::",
            "☷",
            "☰",
        }  # whitespace infront of these strings will be removed
        self.NO_WHITESPACE_AFTER = {
            "{{",
            "::",
            "☷",
            "☰",
        }  # whitespace after of these strings will be removed

        self.ALLOWED_ATTRS = {"src"}  # all other attrs will be removed
        self.RSTRIP_CHARS = (
            " ☷"  # these characters will be treated as whitespace and stripped if needed
        )

        self.__indent_level = 0
        self.__line = ""
        self.__tag = ""
        self.__lines: list[str] = []

    def __attrs_str(self, attrs: list[tuple[str, str | None]]) -> str:
        attrs_list = [
            f"{name}='{escape(value)}'"
            for (name, value) in attrs
            if name in self.ALLOWED_ATTRS and value
        ]

        if attrs_list:
            return " " + " ".join(attrs_list)
        else:
            return ""

    @property
    def __indent(self) -> str:
        return " " * self.INDENT * self.__indent_level

    @property
    def __stripped_line(self) -> str:
        return self.__line.rstrip(self.RSTRIP_CHARS)

    @property
    def __break_line(self) -> bool:
        if not self.__line:
            return True

        if self.__tag in self.NO_BREAK_TAGS:
            return False

        if self.__stripped_line.endswith(
            tuple(f"{tag}>" for tag in (self.ALLOWED_TAGS - self.INLINE_TAGS)),
        ):
            return True

        return False

    def __strip_line(self, tag: str = "") -> bool:
        if self.__stripped_line.endswith(">"):
            return True

        if self.__stripped_line.endswith(tuple(self.NO_WHITESPACE_AFTER)):
            return True

        if tag in {"sub", "sup"}:
            return True

        return False

    def __next_line(self) -> None:
        self.__lines += [self.__line]
        self.__line = ""

    def __append_to_line(self, string: str) -> None:
        self.__line = self.__line + string

    def __append_to_stripped_line(self, string: str) -> None:
        self.__line = self.__stripped_line + string

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            # place directly after last non-whitespace-character of line
            # linebreak if current tag is breakable

            self.__append_to_stripped_line(f"<{tag}{self.__attrs_str(attrs)}>")
            if self.__tag not in self.NO_BREAK_TAGS:
                self.__next_line()
        elif tag == "img":
            # place on new line

            self.__next_line()
            self.__append_to_line(f"{self.__indent}<{tag}{self.__attrs_str(attrs)}>")
        else:  # pragma: no cover
            raise ValueError()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.NO_BREAK_TAGS:
            if self.__break_line:
                self.__next_line()
                self.__append_to_line(f"{self.__indent}<{tag}{self.__attrs_str(attrs)}>")
                self.__tag = tag
            else:
                self.__append_to_line(" ")

                if self.__strip_line(tag=tag):
                    self.__append_to_stripped_line(f"<{tag}{self.__attrs_str(attrs)}>")
                else:
                    self.__append_to_line(f"<{tag}{self.__attrs_str(attrs)}>")

                self.__tag = tag
        else:
            self.__next_line()
            self.__append_to_line(f"{self.__indent}<{tag}{self.__attrs_str(attrs)}>")
            self.__tag = tag
            self.__indent_level += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self.NO_BREAK_TAGS:
            if tag in ("sub", "sup"):
                self.__append_to_stripped_line(f"</{tag}>")
            else:
                self.__append_to_stripped_line(f"</{tag}> ")

            self.__tag = ""
        else:
            self.__indent_level -= 1
            self.__tag = ""

            self.__next_line()
            self.__append_to_line(f"{self.__indent}</{tag}>")

    def handle_data(self, data: str) -> None:
        data = replace_symbols(data)

        if data.startswith(tuple(self.NO_WHITESPACE_BEFORE)):
            self.__line = self.__line.rstrip(self.RSTRIP_CHARS)

        if not self.__tag or self.__tag in self.NO_BREAK_TAGS:
            self.__line += data
        else:
            self.__lines += [self.__line]
            self.__line = f"{self.__indent}{data}"

    def get_parsed_string(self) -> str:
        self.__lines += [self.__line]

        return "\n".join(line.rstrip(self.RSTRIP_CHARS) for line in self.__lines if line)


def format_html(html: str) -> str:
    html = preprocess(html)

    parser = HTMLParser()
    parser.feed(html)
    html = parser.get_parsed_string()

    html = postprocess(html)

    return html
