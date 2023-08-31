from __future__ import annotations

import os
import sys
from html import escape
from html.parser import HTMLParser as PythonHTMLParser
from typing import NamedTuple
from unittest.mock import MagicMock

if "pytest" in sys.modules:  # pragma: no cover
    aqt = MagicMock()
    aqt.mw.addonManager.getConfig.return_value = {
        "imageOcclusionSVG": {
            "backgroundActive": "#FF7E7E",
            "backgroundInactive": "#FFEBA2",
            "stroke": {
                "active": True,
                "color": "#2D2D2D",
                "width": 1,
            },
        },
    }
    sys.modules["aqt"] = aqt

from aqt import mw
from bs4 import BeautifulSoup
from bs4 import Comment
from bs4 import Tag

from anki_formatter.formatters.common import attrs
from anki_formatter.formatters.common import format_number
from anki_formatter.formatters.common import get_child_tags
from anki_formatter.formatters.common import get_classes
from anki_formatter.formatters.common import strip_whitespace_between_tags
from anki_formatter.formatters.html import format_html

CONFIG = mw.addonManager.getConfig(__name__)["imageOcclusionSVG"]

STROKE: bool = CONFIG["stroke"]["active"]
STROKE_COLOR: str = CONFIG["stroke"]["color"]
STROKE_WIDTH: int | float = format_number(CONFIG["stroke"]["width"])

BACKGROUND_ACTIVE: str = CONFIG["backgroundActive"]
BACKGROUND_INACTIVE: str = CONFIG["backgroundInactive"]


def _title_tag(title: str) -> Tag:
    element = Tag(name="title")
    element.string = title

    return element


class LabelGroup(NamedTuple):
    id: str | None

    title: str | None

    labels: list[Label | LabelGroup]

    @classmethod
    def from_tag(cls, tag: Tag, main_group: bool = False) -> LabelGroup:
        labels: list[Label | LabelGroup] = []

        for child in get_child_tags(tag):
            if child.name == "title":
                continue
            elif child.name == "text":
                labels.append(Label.from_tag(child))
            elif child.name == "g":
                labels.append(LabelGroup.from_tag(child))
            else:
                raise NotImplementedError  # pragma: no cover

        return LabelGroup(
            id="labels" if main_group else None,
            title="Labels" if main_group else None,
            labels=labels,
        )

    def to_tag(self) -> Tag:
        group_element = Tag(name="g", attrs=attrs({"id": self.id}))

        if self.title:
            group_element.append(_title_tag(self.title))

        for label in self.labels:
            group_element.append(label.to_tag())

        return group_element


class Label(NamedTuple):
    x: int | float
    y: int | float
    anchor: str

    font_size: int | float
    font_color: str

    text: str

    @classmethod
    def from_tag(cls, tag: Tag) -> Label:
        return Label(
            x=format_number(tag.attrs.get("x", "0")),
            y=format_number(tag.attrs.get("y", "0")),
            anchor=tag.attrs.get("text-anchor", "middle"),
            font_size=format_number(tag.attrs.get("font-size", "20")),
            font_color=tag.attrs.get("fill", "#000000"),
            text=tag.text,
        )

    def to_tag(self) -> Tag:
        element = Tag(
            name="text",
            attrs=attrs(
                {
                    "x": self.x,
                    "y": self.y,
                    "text-anchor": self.anchor,
                    "font-family": "Arial",
                    "font-size": self.font_size,
                    "fill": self.font_color,
                },
            ),
        )
        element.string = self.text

        return element


class MaskGroup(NamedTuple):
    id: str | None

    title: str | None

    active: bool

    masks: list[Mask | MaskGroup]

    @classmethod
    def from_tag(
        cls,
        tag: Tag,
        svg_width: int | float,
        svg_height: int | float,
        main_group: bool = False,
    ) -> MaskGroup:
        masks: list[Mask | MaskGroup] = []

        for child in get_child_tags(tag):
            if child.name == "title":
                continue
            elif child.name == "rect":
                masks.append(Mask.from_tag(child, svg_width=svg_width, svg_height=svg_height))
            elif child.name == "g":
                masks.append(MaskGroup.from_tag(child, svg_width=svg_width, svg_height=svg_height))
            else:
                raise NotImplementedError  # pragma: no cover

        return MaskGroup(
            id="masks" if main_group else tag.attrs.get("id"),
            title="Masks" if main_group else None,
            active="qshape" in get_classes(tag),
            masks=masks,
        )

    def to_tag(self) -> Tag:
        group_element = Tag(
            name="g",
            attrs=attrs({"id": self.id, "class": "qshape" if self.active else None}),
        )

        if self.title:
            group_element.append(_title_tag(self.title))

        for mask in sorted(
            self.masks,
            key=lambda mask: int(mask.id.split("-")[2]) if mask.id else 0,
        ):
            group_element.append(mask.to_tag())

        return group_element


class Mask(NamedTuple):
    id: str | None

    active: bool

    x: int | float
    y: int | float

    width: int | float
    height: int | float

    @classmethod
    def from_tag(cls, tag: Tag, svg_width: int | float, svg_height: int | float) -> Mask:
        width = format_number(tag.attrs["width"])
        height = format_number(tag.attrs["height"])

        x = format_number(
            tag.attrs.get("x", "0"),
            lower_limit=STROKE_WIDTH / 2 if STROKE else 0,
            upper_limit=svg_width - width - STROKE_WIDTH / 2 if STROKE else svg_width - width,
        )
        y = format_number(
            tag.attrs.get("y", "0"),
            lower_limit=STROKE_WIDTH / 2 if STROKE else 0,
            upper_limit=svg_height - height - STROKE_WIDTH / 2 if STROKE else svg_height - height,
        )

        return Mask(
            id=tag.attrs.get("id"),
            active="qshape" in get_classes(tag),
            x=x,
            y=y,
            width=width,
            height=height,
        )

    def to_tag(self) -> Tag:
        return Tag(
            name="rect",
            attrs=attrs(
                {
                    "id": self.id,
                    "x": self.x,
                    "y": self.y,
                    "width": self.width,
                    "height": self.height,
                    "fill": BACKGROUND_ACTIVE if self.active else BACKGROUND_INACTIVE,
                    "stroke": STROKE_COLOR if STROKE else None,
                    "stroke-width": STROKE_WIDTH if STROKE else None,
                    "class": "qshape" if self.active else None,
                },
            ),
        )


class SVG(NamedTuple):
    labels: LabelGroup
    masks: MaskGroup

    width: int | float
    height: int | float

    @classmethod
    def from_tag(cls, tag: Tag) -> SVG:
        width = format_number(tag.attrs["width"])
        height = format_number(tag.attrs["height"])

        for child in get_child_tags(tag):
            if child.name == "g":
                if child.title:
                    if child.title.text == "Masks":
                        masks = MaskGroup.from_tag(
                            child,
                            svg_width=width,
                            svg_height=height,
                            main_group=True,
                        )
                    elif child.title.text == "Labels":
                        labels = LabelGroup.from_tag(child, main_group=True)
                    else:
                        raise NotImplementedError  # pragma: no cover
                else:
                    raise ValueError  # pragma: no cover
            else:
                raise NotImplementedError  # pragma: no cover

        return SVG(
            labels=labels,
            masks=masks,
            width=width,
            height=height,
        )

    def to_tag(self) -> Tag:
        svg_element = Tag(
            name="svg",
            attrs=attrs(
                {
                    "xmlns": "http://www.w3.org/2000/svg",
                    "width": self.width,
                    "height": self.height,
                },
            ),
        )

        svg_element.append(Comment("Created with Image Occlusion Enhanced"))
        svg_element.append(self.labels.to_tag())
        svg_element.append(self.masks.to_tag())

        return svg_element


class SVGFormatter(PythonHTMLParser):
    def __init__(self) -> None:
        super().__init__()

        self.INDENT = 2
        self.ATTRS_ORDER = [
            "id",
            "x",
            "y",
            "text-anchor",
            "width",
            "height",
            "font-family",
            "font-size",
            "fill",
            "stroke",
            "stroke-width",
            "xmlns",
            "class",
        ]

        self.__indent_level = 0
        self.__line = ""
        self.__tag = ""
        self.__lines: list[str] = []

    def __attrs_str(self, attrs: list[tuple[str, str | None]]) -> str:
        attrs_list = [
            f"{name}='{escape(value)}'"
            for (name, value) in sorted(attrs, key=lambda item: self.ATTRS_ORDER.index(item[0]))
            if value
        ]

        if attrs_list:
            return " " + " ".join(attrs_list)
        else:
            return ""

    @property
    def __indent(self) -> str:
        return " " * self.INDENT * self.__indent_level

    def __next_line(self) -> None:
        self.__lines += [self.__line]
        self.__line = ""

    def __append_to_line(self, string: str) -> None:
        self.__line = self.__line + string

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.__next_line()

        if tag == "rect":
            self.__append_to_line(f"{self.__indent}<{tag}{self.__attrs_str(attrs)}/>")
        else:
            self.__append_to_line(f"{self.__indent}<{tag}{self.__attrs_str(attrs)}>")
            self.__tag = tag

            if tag in ("title", "text"):
                return
            else:
                self.__indent_level += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "rect":
            return
        else:
            self.__tag = ""

            if tag in ("title", "text"):
                self.__append_to_line(f"</{tag}>")
            else:
                self.__indent_level -= 1
                self.__next_line()
                self.__append_to_line(f"{self.__indent}</{tag}>")

    def handle_comment(self, data: str) -> None:
        self.handle_data(f"<!-- {data} -->")

    def handle_data(self, data: str) -> None:
        if not self.__tag or self.__tag in ("title", "text"):
            self.__line += data
        else:
            self.__lines += [self.__line]
            self.__line = f"{self.__indent}{data}"

    def get_parsed_string(self) -> str:
        self.__lines += [self.__line]

        return "\n".join(line.rstrip() for line in self.__lines if line)


def postprocess(soup: BeautifulSoup) -> str:
    soup.smooth()

    text = soup.prettify()
    text = strip_whitespace_between_tags(text)
    text = text.replace("\n", " ")
    text = text.strip()

    return text


def format_image_occlusion_svg(svg: str) -> str:
    original_soup = BeautifulSoup(svg, "html.parser")

    if (
        len(original_soup.contents) != 1
        or not original_soup.svg
        or not isinstance(original_soup.svg, Tag)
    ):
        raise ValueError  # pragma: no cover

    new_soup = BeautifulSoup("", "html.parser")
    new_soup.append(SVG.from_tag(original_soup.svg).to_tag())

    svg = postprocess(new_soup)

    formatter = SVGFormatter()
    formatter.feed(svg)

    return formatter.get_parsed_string()


def format_image_occlusion_field(value: str) -> tuple[str, bool]:  # pragma: no cover
    formatted_value, _ = format_html(value)

    soup = BeautifulSoup(formatted_value, "html.parser")

    if (
        len(soup.contents) != 1
        or not soup.img
        or not isinstance(soup.img, Tag)
        or not soup.img.is_empty_element
    ):
        raise ValueError

    img_src = os.path.join(mw.pm.profileFolder(), "collection.media", soup.img.attrs["src"])

    with open(img_src, encoding="utf-8") as f:
        svg = f.read()

    formatted_svg = format_image_occlusion_svg(svg)

    if svg != formatted_svg:
        with open(img_src, mode="w", encoding="utf-8") as f:
            f.write(formatted_svg)

    return formatted_value, svg != formatted_svg
