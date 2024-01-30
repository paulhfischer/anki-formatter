from __future__ import annotations

import re
import warnings
from html import escape
from html.parser import HTMLParser as PythonHTMLParser

from bs4 import BeautifulSoup

from anki_formatter.formatters.common import fix_encoding
from anki_formatter.formatters.common import replace_symbols
from anki_formatter.formatters.common import strip_whitespace_between_tags

ALLOWED_TAGS = {
    "section",
    "ul",
    "ol",
    "li",
    "strong",
    "em",
    "sub",
    "sup",
    "br",
    "img",
    "anki-mathjax",
}


def _preserve_whitespace(text: str) -> str:
    for tag in ("strong", "b", "em", "i", "sub", "sup"):
        # move whitespace out of tag
        text = text.replace(f" </{tag}>", f"</{tag}> ").replace(f"&nbsp;</{tag}>", f"</{tag}> ")
        text = text.replace(f"<{tag}> ", f" <{tag}>").replace(f"<{tag}>&nbsp;", f" <{tag}>")

        # preserve whitespace before and after formatting-tags
        text = re.sub(rf"</{tag}>(?: \n*)+<{tag}>", f"</{tag}>☰<{tag}>", text)
        text = re.sub(rf"</{tag}>(?:&nbsp;\n*)+<{tag}>", f"</{tag}>☰<{tag}>", text)
        text = text.replace(f"</{tag}> ", f"</{tag}>☷").replace(f"</{tag}>&nbsp;", f"</{tag}>☷")
        text = text.replace(f" <{tag}>", f"☷<{tag}>").replace(f"&nbsp;<{tag}>", f"☷<{tag}>")

    # merge preserved whitspace
    text = re.sub(r"☷+", "☷", text)
    text = re.sub(r"☰+", "☰", text)
    text = re.sub(r"☷☰", "☰", text)

    return text


def preprocess(text: str) -> str:
    text = fix_encoding(text)

    text = _preserve_whitespace(text)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        soup = BeautifulSoup(text, "html.parser")

    # use semantic tags
    for tag in soup.find_all("b"):
        tag.name = "strong"
    for tag in soup.find_all("i"):
        tag.name = "em"

    # remove unwanted tags
    for tag in soup.find_all():
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()

    # remove empty tags
    for tag in soup.find_all():
        if (
            len(tag.get_text(strip=True)) == 0
            and len([content for content in tag.contents if content != "\n"]) == 0
            and tag.name not in {"br", "img"}
        ):
            tag.extract()

    soup.smooth()
    text = soup.prettify()

    text = strip_whitespace_between_tags(text)
    text = text.replace("\n", " ")
    text = text.strip()

    return text


def postprocess(text: str) -> str:
    for tag in ("strong", "em", "sub", "sup"):
        # remove unwanted whitespace between tags and merge them
        text = re.sub(f"</{tag}>(?: )*<{tag}>", "", text)

        # undo preserve whitespace before and after formatting-tags
        text = re.sub(rf"</{tag}> *", f"</{tag}>", text)
        text = text.replace(f"</{tag}>☰<{tag}>", f"</{tag}> <{tag}>")
        text = text.replace(f"</{tag}>☷", f"</{tag}> ")
        text = text.replace(f"☷<{tag}>", f" <{tag}>")

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
            "strong",
            "em",
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

        if data.startswith(("☷", "☰")) and data[1:].startswith(tuple(self.NO_WHITESPACE_BEFORE)):
            data = data[1:]

        if data.startswith(tuple(self.NO_WHITESPACE_BEFORE)):
            self.__line = self.__line.rstrip(self.RSTRIP_CHARS)

        if not self.__tag or self.__tag in self.NO_BREAK_TAGS:
            if not self.__line:
                self.__line += data.lstrip("☷☰")
            else:
                self.__line += data
        else:
            self.__next_line()
            self.__line = f"{self.__indent}{data.lstrip('☷☰')}"

    def get_parsed_string(self) -> str:
        self.__lines += [self.__line]

        return "\n".join(line.rstrip(self.RSTRIP_CHARS) for line in self.__lines if line)


def format_html(html: str) -> tuple[str, bool]:
    formatted_html = preprocess(html)

    parser = HTMLParser()
    parser.feed(formatted_html)
    formatted_html = parser.get_parsed_string()

    formatted_html = postprocess(formatted_html)

    return formatted_html, html != formatted_html
