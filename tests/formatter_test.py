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
        ("<strong>foo</strong> bar", "foo bar"),
        ("<strong>foo</strong>bar", "foobar"),
        ("foo&nbsp;bar", "foo bar"),
        ("foo\u00adbar", "foobar"),
    ),
)
def test_plaintext_formatter(input: str, expected_output: str) -> None:
    ret, _ = convert_to_plaintext(input)

    assert ret == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("foobar", "foobar"),
        ("<strong>foo</strong> bar", "<strong>foo</strong> bar"),
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
        ("text with <strong>important</strong> part.", "text with <strong>important</strong> part."),
        (
            "<section><img src='foo.jpg'><img src='foo.jpg'></section>",
            "<section>\n  <img src='foo.jpg'>\n  <img src='foo.jpg'>\n</section>",
        ),
        (
            "<section>text <strong>with important</strong> part!</section>",
            "<section>\n  text <strong>with important</strong> part!\n</section>",
        ),
        (
            "<section><img src='foo.jpg'><br><img src='bar.jpg'></section>",
            "<section>\n  <img src='foo.jpg'><br>\n  <img src='bar.jpg'>\n</section>",
        ),
        (
            "<section><img src='foo.jpg'><br><strong>important</strong> info</section>",
            "<section>\n  <img src='foo.jpg'><br>\n  <strong>important</strong> info\n</section>",
        ),
        ("<li><strong>foo</strong> bar</li>", "<li><strong>foo</strong> bar</li>"),
        ("<li><strong>a</strong> foo\nbar</li>", "<li><strong>a</strong> foo bar</li>"),
        ("<strong>foo</strong>?", "<strong>foo</strong>?"),
        ("{{c1:: <strong>foo</strong> }} bar", "{{c1::<strong>foo</strong>}} bar"),
        ("{{c1::<strong>foo</strong>}} bar", "{{c1::<strong>foo</strong>}} bar"),
        ("<strong>foo</strong><strong>bar</strong>", "<strong>foobar</strong>"),
        ("<strong>foo</strong> <strong>bar</strong>", "<strong>foo</strong> <strong>bar</strong>"),
        ("A <sub>B</sub> C", "A<sub>B</sub> C"),
        ("A<sub>B</sub> C", "A<sub>B</sub> C"),
        ("A<sub>B</sub>-C", "A<sub>B</sub>-C"),
        ("<li><strong>foo</strong></li>", "<li><strong>foo</strong></li>"),
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
        ("<strong>foo</strong>  <strong>bar</strong>", "<strong>foo</strong> <strong>bar</strong>"),
        ("<strong>foo </strong><strong>bar</strong>", "<strong>foo</strong> <strong>bar</strong>"),
        ("<strong>foo </strong>\n<strong>bar</strong>", "<strong>foo</strong> <strong>bar</strong>"),
        ("<strong>foo</strong>bar", "<strong>foo</strong>bar"),
        ("<strong>foo</strong>-bar", "<strong>foo</strong>-bar"),
        ("<strong>foo</strong> -bar", "<strong>foo</strong> -bar"),
        ("foo<strong>bar</strong>", "foo<strong>bar</strong>"),
        ("foo-<strong>bar</strong>", "foo-<strong>bar</strong>"),
        ("foo- <strong>bar</strong>", "foo- <strong>bar</strong>"),
        ("foo<br><strong>bar</strong>", "foo<br>\n<strong>bar</strong>"),
        ("foo<br> <strong>bar</strong>", "foo<br>\n<strong>bar</strong>"),
        ("<section>foo<br><strong>bar</strong></section>", "<section>\n  foo<br>\n  <strong>bar</strong>\n</section>"),
        ("<section>foo<br> <strong>bar</strong></section>", "<section>\n  foo<br>\n  <strong>bar</strong>\n</section>"),
        ("foo&nbsp;<strong>bar</strong>", "foo <strong>bar</strong>"),
        ("foo<strong>&nbsp;bar</strong>", "foo <strong>bar</strong>"),
        ("foo<sub>bar</sub>&nbsp;foo", "foo<sub>bar</sub> foo"),
        ("foo <em>bar</em> foobar", "foo <em>bar</em> foobar"),
        ("<b>foobar</b>", "<strong>foobar</strong>"),
        ("<i>foobar</i>", "<em>foobar</em>"),
        ("foo <b>foobar</b> bar", "foo <strong>foobar</strong> bar"),
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
