from __future__ import annotations

import pytest

from anki_formatter.formatters.clear import clear
from anki_formatter.formatters.html import format_html
from anki_formatter.formatters.image_occlusion_svg import format_image_occlusion_svg
from anki_formatter.formatters.occlusion import format_occlusion
from anki_formatter.formatters.plaintext import convert_to_plaintext
from anki_formatter.formatters.skip import skip


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (("foobar", ""),),
)
def test_clear_formatter(input: str, expected_output: str) -> None:
    ret, _ = clear(input)

    assert ret == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("foobar", "foobar"),
        ("<b>foo</b> bar", "foo bar"),
        ("<b>foo</b>bar", "foobar"),
        ("foo&nbsp;bar", "foo bar"),
        ("foo\u00adbar", "foobar"),
        ("NAD<sup>+</sup> + P<sub>i</sub>", "NAD⁺ + Pᵢ"),
    ),
)
def test_plaintext_formatter(input: str, expected_output: str) -> None:
    ret, _ = convert_to_plaintext(input)

    assert ret == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("foobar", "foobar"),
        ("<b>foo</b> bar", "<b>foo</b> bar"),
    ),
)
def test_skip_formatter(input: str, expected_output: str) -> None:
    ret, _ = skip(input)

    assert ret == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("{{c1::foo}} {{c2::bar}}", "{{c1::foo}}{{c2::bar}}"),
        ("{{c2::bar}}{{c1::foo}}", "{{c1::foo}}{{c2::bar}}"),
    ),
)
def test_occlusion_formatter(input: str, expected_output: str) -> None:
    ret, _ = format_occlusion(input)

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
        (
            "text with <b>important</b> part.",
            "text with <b>important</b> part.",
        ),
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
        ("„foo“", '"foo"'),
        ("<img src='„foo“'>", "<img src='„foo“'>"),
        ("<li>„foo“</li>", '<li>"foo"</li>'),
        ("<li>foo</li><li></li>", "<li>foo</li>"),
        ("<ul>\n  <li>foo</li>\n  <li>\n    \n  </li>\n</ul>", "<ul>\n  <li>foo</li>\n</ul>"),
        ("<li>foo =&gt; foo&nbsp;bar</li>", "<li>foo ⇒ foo bar</li>"),
        ("<b>foo</b>  <b>bar</b>", "<b>foo</b> <b>bar</b>"),
        ("<b>foo </b><b>bar</b>", "<b>foo</b> <b>bar</b>"),
        (
            "<b>foo </b>\n<b>bar</b>",
            "<b>foo</b> <b>bar</b>",
        ),
        ("<b>foo</b>bar", "<b>foo</b>bar"),
        ("<b>foo</b>-bar", "<b>foo</b>-bar"),
        ("<b>foo</b> -bar", "<b>foo</b> -bar"),
        ("foo<b>bar</b>", "foo<b>bar</b>"),
        ("foo-<b>bar</b>", "foo-<b>bar</b>"),
        ("foo- <b>bar</b>", "foo- <b>bar</b>"),
        ("foo<br><b>bar</b>", "foo<br>\n<b>bar</b>"),
        ("foo<br> <b>bar</b>", "foo<br>\n<b>bar</b>"),
        (
            "<section>foo<br><b>bar</b></section>",
            "<section>\n  foo<br>\n  <b>bar</b>\n</section>",
        ),
        (
            "<section>foo<br> <b>bar</b></section>",
            "<section>\n  foo<br>\n  <b>bar</b>\n</section>",
        ),
        ("foo&nbsp;<b>bar</b>", "foo <b>bar</b>"),
        ("foo<b>&nbsp;bar</b>", "foo <b>bar</b>"),
        ("foo<sub>bar</sub>&nbsp;foo", "foo<sub>bar</sub> foo"),
        ("foo <i>bar</i> foobar", "foo <i>bar</i> foobar"),
        ("<strong>foobar</strong>", "<b>foobar</b>"),
        ("<em>foobar</em>", "<i>foobar</i>"),
        ("<ins>foobar</ins>", "<u>foobar</u>"),
        ("foo <strong>foobar</strong> bar", "foo <b>foobar</b> bar"),
        ("<ol>\n  <li>foo</li>\n</ol>", "<ol>\n  <li>foo</li>\n</ol>"),
        ("<ol start='2'>\n  <li>foo</li>\n</ol>", "<ol start='2'>\n  <li>foo</li>\n</ol>"),
        ("NAD⁺ + Pᵢ", "NAD<sup>+</sup> + P<sub>i</sub>"),
        (r"\[A <=> B\]", r"\[A <=> B\]"),
        (r"\(A <=> B\)", r"\(A <=> B\)"),
        (r"foo <=> bar \[A <=> B\]", r"foo ⇔ bar \[A <=> B\]"),
        (r"foo <=> bar \(A <=> B\)", r"foo ⇔ bar \(A <=> B\)"),
        (r"\[A <=> B\] foo <=> bar", r"\[A <=> B\] foo ⇔ bar"),
        (r"\(A <=> B\) foo <=> bar", r"\(A <=> B\) foo ⇔ bar"),
        (r"foo <=> bar \[A <=> B\] foo <=> bar", r"foo ⇔ bar \[A <=> B\] foo ⇔ bar"),
        (r"foo <=> bar \(A <=> B\) foo <=> bar", r"foo ⇔ bar \(A <=> B\) foo ⇔ bar"),
    ),
)
def test_html_formatter(input: str, expected_output: str) -> None:
    ret, _ = format_html(input)

    assert ret == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        # masks: reorder and strip attributes
        (
            """\
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="1500">
 <!-- Created with Image Occlusion Enhanced -->
 <g>
  <title>Labels</title>
 </g>
 <g>
  <title>Masks</title>
  <rect fill="#FFEBA2" stroke="#2D2D2D" x="167" y="209" width="260" height="135" id="628be4152337460db5e8d5e58c13425a-ao-1" stroke-linecap="null"/>
 </g>
</svg>""",  # noqa: E501
            """\
<svg width='500' height='1500' xmlns='http://www.w3.org/2000/svg'>
  <!-- Created with Image Occlusion Enhanced -->
  <g id='labels'>
    <title>Labels</title>
  </g>
  <g id='masks'>
    <title>Masks</title>
    <rect id='628be4152337460db5e8d5e58c13425a-ao-1' x='167' y='209' width='260' height='135' fill='#FFEBA2' stroke='#2D2D2D' stroke-width='1'/>
  </g>
</svg>""",  # noqa: E501
        ),
        # masks: round dimensions
        (
            """\
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="1500">
 <!-- Created with Image Occlusion Enhanced -->
 <g>
  <title>Labels</title>
 </g>
 <g>
  <title>Masks</title>
  <rect id="628be4152337460db5e8d5e58c13425a-ao-1" x="-2" y="1370" width="260.7" height="135.3" fill="#FFEBA2" stroke="#2D2D2D" stroke-width="1"/>
 </g>
</svg>""",  # noqa: E501
            """\
<svg width='500' height='1500' xmlns='http://www.w3.org/2000/svg'>
  <!-- Created with Image Occlusion Enhanced -->
  <g id='labels'>
    <title>Labels</title>
  </g>
  <g id='masks'>
    <title>Masks</title>
    <rect id='628be4152337460db5e8d5e58c13425a-ao-1' x='0.5' y='1364.5' width='261' height='135' fill='#FFEBA2' stroke='#2D2D2D' stroke-width='1'/>
  </g>
</svg>""",  # noqa: E501
        ),
        # masks: respect active state
        (
            """\
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="1500">
 <!-- Created with Image Occlusion Enhanced -->
 <g>
  <title>Labels</title>
 </g>
 <g>
  <title>Masks</title>
  <rect id="628be4152337460db5e8d5e58c13425a-ao-1" x="167" y="209" width="260" height="135" fill="#FF7E7E" stroke="#2D2D2D" stroke-width="1" class="qshape"/>
 </g>
</svg>""",  # noqa: E501
            """\
<svg width='500' height='1500' xmlns='http://www.w3.org/2000/svg'>
  <!-- Created with Image Occlusion Enhanced -->
  <g id='labels'>
    <title>Labels</title>
  </g>
  <g id='masks'>
    <title>Masks</title>
    <rect id='628be4152337460db5e8d5e58c13425a-ao-1' x='167' y='209' width='260' height='135' fill='#FF7E7E' stroke='#2D2D2D' stroke-width='1' class='qshape'/>
  </g>
</svg>""",  # noqa: E501
        ),
        # masks: sort
        (
            """\
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="1500">
 <!-- Created with Image Occlusion Enhanced -->
 <g>
  <title>Labels</title>
 </g>
 <g>
  <title>Masks</title>
  <rect id="628be4152337460db5e8d5e58c13425a-ao-2" x="29" y="1067" width="260" height="135" fill="#FFEBA2" stroke="#2D2D2D" stroke-width="1"/>
  <rect id="628be4152337460db5e8d5e58c13425a-ao-1" x="167" y="209" width="260" height="135" fill="#FFEBA2" stroke="#2D2D2D" stroke-width="1"/>
 </g>
</svg>""",  # noqa: E501
            """\
<svg width='500' height='1500' xmlns='http://www.w3.org/2000/svg'>
  <!-- Created with Image Occlusion Enhanced -->
  <g id='labels'>
    <title>Labels</title>
  </g>
  <g id='masks'>
    <title>Masks</title>
    <rect id='628be4152337460db5e8d5e58c13425a-ao-1' x='167' y='209' width='260' height='135' fill='#FFEBA2' stroke='#2D2D2D' stroke-width='1'/>
    <rect id='628be4152337460db5e8d5e58c13425a-ao-2' x='29' y='1067' width='260' height='135' fill='#FFEBA2' stroke='#2D2D2D' stroke-width='1'/>
  </g>
</svg>""",  # noqa: E501
        ),
        # masks: groups
        (
            """\
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="1500">
 <!-- Created with Image Occlusion Enhanced -->
 <g>
  <title>Labels</title>
 </g>
 <g>
  <title>Masks</title>
  <g id="628be4152337460db5e8d5e58c13425a-ao-1">
    <rect x="29" y="1067" width="260" height="135" fill="#FFEBA2" stroke="#2D2D2D" stroke-width="1"/>
    <rect x="167" y="209" width="260" height="135" fill="#FFEBA2" stroke="#2D2D2D" stroke-width="1"/>
  </g>
 </g>
</svg>""",  # noqa: E501
            """\
<svg width='500' height='1500' xmlns='http://www.w3.org/2000/svg'>
  <!-- Created with Image Occlusion Enhanced -->
  <g id='labels'>
    <title>Labels</title>
  </g>
  <g id='masks'>
    <title>Masks</title>
    <g id='628be4152337460db5e8d5e58c13425a-ao-1'>
      <rect x='29' y='1067' width='260' height='135' fill='#FFEBA2' stroke='#2D2D2D' stroke-width='1'/>
      <rect x='167' y='209' width='260' height='135' fill='#FFEBA2' stroke='#2D2D2D' stroke-width='1'/>
    </g>
  </g>
</svg>""",  # noqa: E501
        ),
        # labels: reorder and strip attributes
        (
            """\
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="1500">
 <!-- Created with Image Occlusion Enhanced -->
 <g>
  <title>Labels</title>
  <text xml:space="preserve" text-anchor="middle" font-family="'Arial', 'Helvetica LT Std', Arial, sans-serif" font-size="24" y="110" x="400" fill="#000000">foobar</text>
 </g>
 <g>
  <title>Masks</title>
 </g>
</svg>""",  # noqa: E501
            """\
<svg width='500' height='1500' xmlns='http://www.w3.org/2000/svg'>
  <!-- Created with Image Occlusion Enhanced -->
  <g id='labels'>
    <title>Labels</title>
    <text x='400' y='110' text-anchor='middle' font-family='Arial' font-size='24' fill='#000000'>foobar</text>
  </g>
  <g id='masks'>
    <title>Masks</title>
  </g>
</svg>""",  # noqa: E501
        ),
        # labels: round dimensions
        (
            """\
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="1500">
 <!-- Created with Image Occlusion Enhanced -->
 <g>
  <title>Labels</title>
  <text x="400.3" y="110.7" text-anchor="middle" font-family="Arial" font-size="24" fill="#000000">foobar</text>
 </g>
 <g>
  <title>Masks</title>
 </g>
</svg>""",  # noqa: E501
            """\
<svg width='500' height='1500' xmlns='http://www.w3.org/2000/svg'>
  <!-- Created with Image Occlusion Enhanced -->
  <g id='labels'>
    <title>Labels</title>
    <text x='400' y='111' text-anchor='middle' font-family='Arial' font-size='24' fill='#000000'>foobar</text>
  </g>
  <g id='masks'>
    <title>Masks</title>
  </g>
</svg>""",  # noqa: E501
        ),
        # labels: groups
        (
            """\
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="1500">
 <!-- Created with Image Occlusion Enhanced -->
 <g>
  <title>Labels</title>
  <g>
    <text x="400" y="110" text-anchor="middle" font-family="Arial" font-size="24" fill="#000000">foo</text>
    <text x="200" y="60" text-anchor="middle" font-family="Arial" font-size="24" fill="#000000">bar</text>
  </g>
 </g>
 <g>
  <title>Masks</title>
 </g>
</svg>""",  # noqa: E501
            """\
<svg width='500' height='1500' xmlns='http://www.w3.org/2000/svg'>
  <!-- Created with Image Occlusion Enhanced -->
  <g id='labels'>
    <title>Labels</title>
    <g>
      <text x='400' y='110' text-anchor='middle' font-family='Arial' font-size='24' fill='#000000'>foo</text>
      <text x='200' y='60' text-anchor='middle' font-family='Arial' font-size='24' fill='#000000'>bar</text>
    </g>
  </g>
  <g id='masks'>
    <title>Masks</title>
  </g>
</svg>""",  # noqa: E501
        ),
    ),
)
def test_image_occlusion_svg_formatter(input: str, expected_output: str) -> None:
    ret = format_image_occlusion_svg(input)

    assert ret == expected_output
