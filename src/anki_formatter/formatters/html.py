from __future__ import annotations

import re
import warnings
from html import escape
from html.parser import HTMLParser as PythonHTMLParser
from itertools import product
from typing import Literal

from bs4 import BeautifulSoup

from anki_formatter.formatters.common import fix_encoding
from anki_formatter.formatters.common import replace_symbols
from anki_formatter.formatters.common import strip_whitespace_between_tags

ALLOWED_TAGS = {
    "section",
    "ul",
    "ol",
    "li",
    "b",
    "i",
    "u",
    "ins",
    "sub",
    "sup",
    "br",
    "img",
    "anki-mathjax",
    "table",
    "caption",
    "tbody",
    "colgroup",
    "col",
    "td",
    "tr",
}

FORMATTING_TAGS = {
    "strong",
    "b",
    "em",
    "i",
    "ins",
    "u",
    "sub",
    "sup",
}

EMPTY_TAGS = {
    "br",
    "img",
    "col",
    "td",
}


def _preserve_whitespace(text: str) -> str:
    text = text.replace("&nbsp;", " ")

    # move whitespace out of tag
    for tag in FORMATTING_TAGS:
        text = text.replace(f" </{tag}>", f"</{tag}> ")
        text = text.replace(f"<{tag}> ", f" <{tag}>")

    # preserve whitespace before and after formatting-tags
    for tag_1, tag_2 in product(FORMATTING_TAGS, repeat=2):
        text = re.sub(rf"</{tag_1}>(?: \n*)+<{tag_2}>", f"</{tag_1}>☰<{tag_2}>", text)
    for tag in FORMATTING_TAGS:
        text = text.replace(f"</{tag}> ", f"</{tag}>☷")
        text = text.replace(f" <{tag}>", f"☷<{tag}>")

    # merge preserved whitspace
    text = re.sub(r"☷+", "☷", text)
    text = re.sub(r"[☷☰]+", lambda m: "☰" if "☰" in m.group() else m.group(), text)

    return text


def preprocess(text: str) -> str:
    text = fix_encoding(text)
    text = replace_symbols(text, html=True, tags_only=True)

    text = _preserve_whitespace(text)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        soup = BeautifulSoup(text, "html.parser")

    # use formatting tags
    for tag in soup.find_all("strong"):
        tag.name = "b"
    for tag in soup.find_all("em"):
        tag.name = "i"

    # merge redundant tags
    for tag in FORMATTING_TAGS:
        for outer_tag in soup.find_all(tag):
            nested_tags = outer_tag.find_all(tag, recursive=False)
            for nested in nested_tags:
                nested.unwrap()

    # remove unwanted tags
    for tag in soup.find_all():
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()

    # remove empty tags
    for tag in soup.find_all():
        if (
            len(tag.get_text(strip=True)) == 0
            and len([content for content in tag.contents if content != "\n"]) == 0
            and tag.name not in EMPTY_TAGS
        ):
            tag.extract()

    soup.smooth()
    text = soup.prettify()

    text = strip_whitespace_between_tags(text)
    text = text.replace("\n", " ")
    text = text.strip()

    return text


def postprocess(text: str) -> str:
    # remove unwanted whitespace between and after formatting-tags and merge them
    for tag in FORMATTING_TAGS:
        text = re.sub(f"</{tag}>(?: )*<{tag}>", "", text)
        text = re.sub(rf"</{tag}> *", f"</{tag}>", text)

    # undo preserve whitespace
    text = text.replace("☰", " ")
    text = text.replace("☷", " ")

    # collapse multiple spaces between words and tags
    text = re.sub(r"(?<=\S) +(?=\S)", " ", text)
    text = re.sub(r"(?<=>) +(?=\S)", " ", text)
    text = re.sub(r"(?<=\S) +(?=<)", " ", text)
    text = re.sub(r"(?<=>) +(?=<)", " ", text)

    # remove br at end of li-items
    text = re.sub(r"(?:<br>\s*)+</li>", "</li>", text)

    text = text.rstrip()

    return text


class HTMLParser(PythonHTMLParser):
    def __init__(self) -> None:
        super().__init__()

        self.INDENT = 2
        self.ALLOWED_TAGS = ALLOWED_TAGS  # all other tags will be removed
        self.INLINE_TAGS = FORMATTING_TAGS | {
            "anki-mathjax",
        }  # these tags will be placed on the current line
        self.NO_BREAK_TAGS = self.INLINE_TAGS | {
            "li",
            "caption",
            "td",
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

        self.ALLOWED_ATTRS: dict[tuple[str, str], None | dict[str, set[str] | Literal["*"]]] = {
            ("img", "src"): None,
            ("ol", "start"): None,
            ("col", "style"): {
                "width": "*",
            },
            ("td", "rowspan"): None,
            ("td", "colspan"): None,
            ("td", "style"): {
                "text-align": {"center", "right"},
                "white-space": {"nowrap"},
            },
        }  # all other attrs will be removed

        self.REQUIRED_ATTRS: dict[tuple[str, str], str | dict[str, str]] = {
            ("table", "border"): "1",
            ("table", "style"): {
                "border-collapse": "collapse",
            },
        }  # these attrs will always be set

        self.RSTRIP_CHARS = (
            " ☷"  # these characters will be treated as whitespace and stripped if needed
        )

        self.__indent_level = 0
        self.__line = ""
        self.__tag = ""
        self.__tag_stack: list[str] = []
        self.__lines: list[str] = []

    def __attrs_str(self, tag: str, attrs: list[tuple[str, str | None]]) -> str:
        attrs_list: list[str] = []

        for attr_key, attr_value in attrs:
            if (tag, attr_key) in self.ALLOWED_ATTRS and attr_value:
                rules = self.ALLOWED_ATTRS[(tag, attr_key)]

                if rules is None:
                    attrs_list.append(f"{attr_key}='{escape(attr_value)}'")
                elif isinstance(rules, dict) and attr_key == "style":
                    original_style = {
                        k.strip(): v.strip()
                        for item in attr_value.split(";")
                        if ":" in item
                        for k, v in [item.split(":", 1)]
                    }
                    filtered_style = {
                        key: value
                        for key, value in original_style.items()
                        if key in rules and (rules[key] == "*" or value in rules[key])
                    }
                    attrs_list.append(
                        f"{attr_key}='{escape('; '.join(f'{k}: {v}' for k, v in filtered_style.items()))};'",  # noqa: E501
                    )
                else:  # pragma: no cover
                    raise ValueError

        for (tag_name, required_attr_key), required_attr_value in self.REQUIRED_ATTRS.items():
            if tag_name == tag:
                if isinstance(required_attr_value, str):
                    attrs_list.append(f"{required_attr_key}='{escape(required_attr_value)}'")
                elif isinstance(required_attr_value, dict) and required_attr_key == "style":
                    attrs_list.append(
                        f"{required_attr_key}='{escape('; '.join(f'{k}: {v}' for k, v in required_attr_value.items()))};'",  # noqa: E501
                    )
                else:  # pragma: no cover
                    raise ValueError

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

        if self.__stripped_line.endswith("<br>"):
            return False

        if self.__tag in self.NO_BREAK_TAGS:
            return False

        if re.search(
            rf"({'|'.join(self.ALLOWED_TAGS - self.INLINE_TAGS)})\s*[^>]*?>$",
            self.__stripped_line,
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

            self.__append_to_stripped_line(f"<{tag}{self.__attrs_str(tag, attrs)}>")
            if not (self.__tag_stack and self.__tag_stack[-1] in self.NO_BREAK_TAGS):
                self.__next_line()
        elif tag == "img":
            # place on new line

            self.__next_line()
            self.__append_to_line(f"{self.__indent}<{tag}{self.__attrs_str(tag, attrs)}>")
        elif tag == "col":
            # place on new line

            self.__next_line()
            self.__append_to_line(f"{self.__indent}<{tag}{self.__attrs_str(tag, attrs)}>")
        else:  # pragma: no cover
            raise ValueError()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.NO_BREAK_TAGS:
            if self.__break_line:
                self.__next_line()
                self.__append_to_line(f"{self.__indent}<{tag}{self.__attrs_str(tag, attrs)}>")
            else:
                if self.__strip_line(tag=tag):
                    self.__append_to_stripped_line(f"<{tag}{self.__attrs_str(tag, attrs)}>")
                else:
                    self.__append_to_line(f"<{tag}{self.__attrs_str(tag, attrs)}>")

                self.__tag = tag
        else:
            self.__next_line()
            self.__append_to_line(f"{self.__indent}<{tag}{self.__attrs_str(tag, attrs)}>")
            self.__indent_level += 1

        self.__tag = tag
        self.__tag_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.NO_BREAK_TAGS:
            if tag in ("sub", "sup"):
                self.__append_to_stripped_line(f"</{tag}>")
            else:
                self.__append_to_stripped_line(f"</{tag}> ")
        else:
            self.__indent_level -= 1

            self.__next_line()
            self.__append_to_line(f"{self.__indent}</{tag}>")

        self.__tag = ""
        assert self.__tag_stack and self.__tag_stack[-1] == tag
        self.__tag_stack.pop()

    def handle_data(self, data: str) -> None:
        data = replace_symbols(data, html=True)

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


def format_html(html: str, minimized: bool) -> tuple[str, bool]:
    formatted_html = preprocess(html)

    parser = HTMLParser()
    parser.feed(formatted_html)
    formatted_html = parser.get_parsed_string()

    formatted_html = postprocess(formatted_html)

    if minimized:
        formatted_html = re.sub(r"\n *", "", formatted_html)

    return formatted_html, html != formatted_html
