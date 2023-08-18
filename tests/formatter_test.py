from __future__ import annotations

import pytest

from anki_formatter.formatters.clear import clear
from anki_formatter.formatters.html import format_html
from anki_formatter.formatters.plaintext import convert_to_plaintext
from anki_formatter.formatters.skip import skip


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (("foobar", ""),),
)
def test_clear_formatter(input: str, expected_output: str) -> None:
    ret = clear(input)

    assert ret == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("foobar", "foobar"),
        ("<b>foo</b> bar", "foo bar"),
        ("<b>foo</b>bar", "foobar"),
    ),
)
def test_plaintext_formatter(input: str, expected_output: str) -> None:
    ret = convert_to_plaintext(input)

    assert ret == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("foobar", "foobar"),
        ("<b>foo</b> bar", "<b>foo</b> bar"),
    ),
)
def test_skip_formatter(input: str, expected_output: str) -> None:
    ret = skip(input)

    assert ret == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("foobar", "foobar"),
        ("line1<br>line2", "line1<br>\nline2"),
        ("<img src='foo.jpg'><br>bar", "<img src='foo.jpg'><br>\nbar"),
        ("<li>foo<br>bar</li>", "<li>foo<br>bar</li>"),
        ("<li>foo<br></li>", "<li>foo</li>"),
        ("<div>text</div>", "text"),
        ("<ul><li>foo</li><li>bar</li></ul>", "<ul>\n  <li>foo</li>\n  <li>bar</li>\n</ul>"),
        (
            "<ul><li>foo</li><ul><li>foo</li><li>bar</li></ul></ul>",
            "<ul>\n  <li>foo</li>\n  <ul>\n    <li>foo</li>\n    <li>bar</li>\n  </ul>\n</ul>",
        ),
        ("text with <b>important</b> part.", "text with <b>important</b> part."),
        (
            "<section><img src='foo.jpg'><img src='foo.jpg'></section>",
            "<section>\n  <img src='foo.jpg'>\n  <img src='foo.jpg'>\n</section>",
        ),
        (
            "<section>text <b>with important</b> part!</section>",
            "<section>\n  text <b>with important</b> part!\n</section>",
        ),
        (
            "<section><img src='foo.jpg'><br><img src='bar.jpg'></section>",
            "<section>\n  <img src='foo.jpg'><br>\n  <img src='bar.jpg'>\n</section>",
        ),
        (
            "<section><img src='foo.jpg'><br><b>important</b> info</section>",
            "<section>\n  <img src='foo.jpg'><br>\n  <b>important</b> info\n</section>",
        ),
        ("<li><b>foo</b> bar</li>", "<li><b>foo</b> bar</li>"),
        ("<li><b>a</b> foo\nbar</li>", "<li><b>a</b> foo bar</li>"),
        ("<b>foo</b>?", "<b>foo</b>?"),
        ("{{c1:: <b>foo</b> }} bar", "{{c1::<b>foo</b>}} bar"),
        ("{{c1::<b>foo</b>}} bar", "{{c1::<b>foo</b>}} bar"),
        ("<b>foo</b><b>bar</b>", "<b>foobar</b>"),
        ("<b>foo</b> <b>bar</b>", "<b>foo</b> <b>bar</b>"),
        ("A <sub>B</sub> C", "A<sub>B</sub> C"),
        ("A<sub>B</sub> C", "A<sub>B</sub> C"),
        ("A<sub>B</sub>-C", "A<sub>B</sub>-C"),
        ("<li><b>foo</b></li>", "<li><b>foo</b></li>"),
        ("<li>foobar bar<sub>foo</sub></li>", "<li>foobar bar<sub>foo</sub></li>"),
        ("<li>foo<sub>bar</sub></li>", "<li>foo<sub>bar</sub></li>"),
        ("<li>foo <sub>bar</sub></li>", "<li>foo<sub>bar</sub></li>"),
        ("<li>foo<sub>bar</sub> </li>", "<li>foo<sub>bar</sub></li>"),
        ("<li>foo <sub>bar</sub> </li>", "<li>foo<sub>bar</sub></li>"),
    ),
)
def test_html_formatter(input: str, expected_output: str) -> None:
    ret = format_html(input)

    assert ret == expected_output
