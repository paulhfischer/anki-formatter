from __future__ import annotations

from unittest.mock import Mock
from unittest.mock import patch

import pytest

from anki_formatter.formatters.clear import clear
from anki_formatter.formatters.date import format_date
from anki_formatter.formatters.html import format_html
from anki_formatter.formatters.image_occlusion_svg import format_image_occlusion_svg
from anki_formatter.formatters.links import format_links
from anki_formatter.formatters.meditricks import format_meditricks
from anki_formatter.formatters.occlusion import format_occlusion
from anki_formatter.formatters.plaintext import convert_to_plaintext
from anki_formatter.formatters.skip import skip
from anki_formatter.formatters.source import format_source


def mocked_links_requests(url: str, timeout: int | None = None) -> Mock:
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = {
        "https://de.wikipedia.org/wiki/Golgi-Apparat": "<html><title>Golgi-Apparat – Wikipedia</title></html>",  # noqa: E501
        "https://flexikon.doccheck.com/de/Endoplasmatisches_Retikulum": "<html><title>Endoplasmatisches Retikulum - DocCheck Flexikon</title></html>",  # noqa: E501
    }[url]

    return mock_resp


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("", ""),
        ("foobar", ""),
    ),
)
def test_clear_formatter(input: str, expected_output: str) -> None:
    ret_1, _ = clear(input, False)
    ret_2, _ = clear(ret_1, False)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


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
    ret_1, _ = convert_to_plaintext(input, False)
    ret_2, _ = convert_to_plaintext(ret_1, False)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("foobar", "foobar"),
        ("<b>foo</b> bar", "<b>foo</b> bar"),
    ),
)
def test_skip_formatter(input: str, expected_output: str) -> None:
    ret_1, _ = skip(input, False)
    ret_2, _ = skip(ret_1, False)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("{{c1::foo}} {{c2::bar}}", "{{c1::foo}}{{c2::bar}}"),
        ("{{c2::bar}}{{c1::foo}}", "{{c1::foo}}{{c2::bar}}"),
    ),
)
def test_occlusion_formatter(input: str, expected_output: str) -> None:
    ret_1, _ = format_occlusion(input, False)
    ret_2, _ = format_occlusion(ret_1, False)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        (
            """foobar""",
            """foobar""",
        ),
        (
            """line1<br>line2""",
            """line1<br>\nline2""",
        ),
        (
            """<img src="foo.jpg"><br>bar""",
            """<img src="foo.jpg"><br>\nbar""",
        ),
        (
            """<li>foo<br>bar</li>""",
            """<li>foo<br>bar</li>""",
        ),
        (
            """<li>foo<br></li>""",
            """<li>foo</li>""",
        ),
        (
            """<div>text</div>""",
            """text""",
        ),
        (
            """<ul><li>foo</li><li>bar</li></ul>""",
            """<ul>\n  <li>foo</li>\n  <li>bar</li>\n</ul>""",
        ),
        (
            """<ul><li>foo</li><ul><li>foo</li><li>bar</li></ul></ul>""",
            """<ul>\n  <li>foo</li>\n  <ul>\n    <li>foo</li>\n    <li>bar</li>\n  </ul>\n</ul>""",
        ),
        (
            """text with <b>important</b> part.""",
            """text with <b>important</b> part.""",
        ),
        (
            """<section><img src="foo.jpg"><img src="foo.jpg"></section>""",
            """<section>\n  <img src="foo.jpg">\n  <img src="foo.jpg">\n</section>""",
        ),
        (
            """<section>text <b>with important</b> part!</section>""",
            """<section>\n  text <b>with important</b> part!\n</section>""",
        ),
        (
            """<section><img src="foo.jpg"><br><img src="bar.jpg"></section>""",
            """<section>\n  <img src="foo.jpg"><br>\n  <img src="bar.jpg">\n</section>""",
        ),
        (
            """<section><img src="foo.jpg"><br><b>important</b> info</section>""",
            """<section>\n  <img src="foo.jpg"><br>\n  <b>important</b> info\n</section>""",
        ),
        (
            """<li><b>foo</b> bar</li>""",
            """<li><b>foo</b> bar</li>""",
        ),
        (
            """<li><b>a</b> foo\nbar</li>""",
            """<li><b>a</b> foo bar</li>""",
        ),
        (
            """<b>foo</b>?""",
            """<b>foo</b>?""",
        ),
        (
            """{{c1:: <b>foo</b> }} bar""",
            """{{c1::<b>foo</b>}} bar""",
        ),
        (
            """{{c1::<b>foo</b>}} bar""",
            """{{c1::<b>foo</b>}} bar""",
        ),
        (
            """<b>foo</b><b>bar</b>""",
            """<b>foobar</b>""",
        ),
        (
            """<b>foo</b> <b>bar</b>""",
            """<b>foo bar</b>""",
        ),
        (
            """A <sub>B</sub> C""",
            """A<sub>B</sub> C""",
        ),
        (
            """A<sub>B</sub> C""",
            """A<sub>B</sub> C""",
        ),
        (
            """A<sub>B</sub>-C""",
            """A<sub>B</sub>-C""",
        ),
        (
            """<li><b>foo</b></li>""",
            """<li><b>foo</b></li>""",
        ),
        (
            """<li>foobar bar<sub>foo</sub></li>""",
            """<li>foobar bar<sub>foo</sub></li>""",
        ),
        (
            """<li>foo<sub>bar</sub></li>""",
            """<li>foo<sub>bar</sub></li>""",
        ),
        (
            """<li>foo <sub>bar</sub></li>""",
            """<li>foo<sub>bar</sub></li>""",
        ),
        (
            """<li>foo<sub>bar</sub> </li>""",
            """<li>foo<sub>bar</sub></li>""",
        ),
        (
            """<li>foo <sub>bar</sub> </li>""",
            """<li>foo<sub>bar</sub></li>""",
        ),
        (
            """„foo“""",
            """\"foo\"""",
        ),
        (
            """<img src="„foo“">""",
            """<img src="„foo“">""",
        ),
        (
            """<li>„foo“</li>""",
            """<li>"foo"</li>""",
        ),
        (
            """<li>foo</li><li></li>""",
            """<li>foo</li>""",
        ),
        (
            """<ul>\n  <li>foo</li>\n  <li>\n    \n  </li>\n</ul>""",
            """<ul>\n  <li>foo</li>\n</ul>""",
        ),
        (
            """<li>foo =&gt; foo&nbsp;bar</li>""",
            """<li>foo ⇒ foo bar</li>""",
        ),
        (
            """<b>foo</b>  <b>bar</b>""",
            """<b>foo bar</b>""",
        ),
        (
            """<b>foo </b><b>bar</b>""",
            """<b>foo bar</b>""",
        ),
        (
            """<b>foo </b>\n<b>bar</b>""",
            """<b>foo bar</b>""",
        ),
        (
            """<b>foo</b>bar""",
            """<b>foo</b>bar""",
        ),
        (
            """<b>foo</b>-bar""",
            """<b>foo</b>-bar""",
        ),
        (
            """<b>foo</b> -bar""",
            """<b>foo</b> -bar""",
        ),
        (
            """foo<b>bar</b>""",
            """foo<b>bar</b>""",
        ),
        (
            """foo-<b>bar</b>""",
            """foo-<b>bar</b>""",
        ),
        (
            """foo- <b>bar</b>""",
            """foo- <b>bar</b>""",
        ),
        (
            """foo<br><b>bar</b>""",
            """foo<br>\n<b>bar</b>""",
        ),
        (
            """foo<br> <b>bar</b>""",
            """foo<br>\n<b>bar</b>""",
        ),
        (
            """<section>foo<br><b>bar</b></section>""",
            """<section>\n  foo<br>\n  <b>bar</b>\n</section>""",
        ),
        (
            """<section>foo<br> <b>bar</b></section>""",
            """<section>\n  foo<br>\n  <b>bar</b>\n</section>""",
        ),
        (
            """foo&nbsp;<b>bar</b>""",
            """foo <b>bar</b>""",
        ),
        (
            """foo<b>&nbsp;bar</b>""",
            """foo <b>bar</b>""",
        ),
        (
            """foo<sub>bar</sub>&nbsp;foo""",
            """foo<sub>bar</sub> foo""",
        ),
        (
            """foo <i>bar</i> foobar""",
            """foo <i>bar</i> foobar""",
        ),
        (
            """<strong>foobar</strong>""",
            """<b>foobar</b>""",
        ),
        (
            """<em>foobar</em>""",
            """<i>foobar</i>""",
        ),
        (
            """foo <strong>foobar</strong> bar""",
            """foo <b>foobar</b> bar""",
        ),
        (
            """<ol>\n  <li>foo</li>\n</ol>""",
            """<ol>\n  <li>foo</li>\n</ol>""",
        ),
        (
            """<ol start="2">\n  <li>foo</li>\n</ol>""",
            """<ol start="2">\n  <li>foo</li>\n</ol>""",
        ),
        (
            """NAD⁺ + Pᵢ""",
            """NAD<sup>+</sup> + P<sub>i</sub>""",
        ),
        (
            r"""\[A <=> B\]""",
            r"""\[A <=> B\]""",
        ),
        (
            r"""\(A <=> B\)""",
            r"""\(A <=> B\)""",
        ),
        (
            r"""foo <=> bar \[A <=> B\]""",
            r"""foo ⇔ bar \[A <=> B\]""",
        ),
        (
            r"""foo <=> bar \(A <=> B\)""",
            r"""foo ⇔ bar \(A <=> B\)""",
        ),
        (
            r"""\[A <=> B\] foo <=> bar""",
            r"""\[A <=> B\] foo ⇔ bar""",
        ),
        (
            r"""\(A <=> B\) foo <=> bar""",
            r"""\(A <=> B\) foo ⇔ bar""",
        ),
        (
            r"""foo <=> bar \[A <=> B\] foo <=> bar""",
            r"""foo ⇔ bar \[A <=> B\] foo ⇔ bar""",
        ),
        (
            r"""foo <=> bar \(A <=> B\) foo <=> bar""",
            r"""foo ⇔ bar \(A <=> B\) foo ⇔ bar""",
        ),
        (
            """<b>foo</b>&nbsp;<i>bar</i>""",
            """<b>foo</b> <i>bar</i>""",
        ),
        (
            """<li><b>foo</b><br></li>""",
            """<li><b>foo</b></li>""",
        ),
        (
            """<u>foo<b>bas</b>    bar</u>""",
            """<u>foo<b>bas</b> bar</u>""",
        ),
        (
            """<u>foo   bar</u>""",
            """<u>foo bar</u>""",
        ),
        (
            """<u>foo <u>bar</u></u>""",
            """<u>foo bar</u>""",
        ),
        (
            """<u>foo <ins>bar</ins></u>""",
            """<u>foo <ins>bar</ins></u>""",
        ),
        (
            """<u>foo <u>bar</u> <b>bas</b></u>""",
            """<u>foo bar <b>bas</b></u>""",
        ),
        (
            """<u>foo<b>bas</b> <u>bar</u></u>""",
            """<u>foo<b>bas</b> bar</u>""",
        ),
        (
            """<u>foo<b>bas</b>  <u>bar</u></u>""",
            """<u>foo<b>bas</b> bar</u>""",
        ),
        (
            """<u>foo<b>bas</b> <u> bar</u></u>""",
            """<u>foo<b>bas</b> bar</u>""",
        ),
        (
            """<u>foo<b>bas </b> <b>  bar</b></u>""",
            """<u>foo<b>bas bar</b></u>""",
        ),
        (
            """<u>foo<b>bas </b> <u>  bar</u></u>""",
            """<u>foo<b>bas</b> bar</u>""",
        ),
        (
            """<li>foo<br>bar</li>""",
            """<li>foo<br>bar</li>""",
        ),
        (
            """<li><u>foo</u><u>bar</u></li>""",
            """<li><u>foobar</u></li>""",
        ),
        (
            """<li><u>foo</u><b>bar</b></li>""",
            """<li><u>foo</u><b>bar</b></li>""",
        ),
        (
            """<li><u>foo</u><br><u>bar</u></li>""",
            """<li><u>foo</u><br><u>bar</u></li>""",
        ),
        (
            """<li><u>foo</u><br><b>bar</b></li>""",
            """<li><u>foo</u><br><b>bar</b></li>""",
        ),
        (
            """<table style='border-collapse: collapse'><caption>foobar</caption><colgroup><col style='width: 20%'><col style='width: 80%; height: 32px'></colgroup><tbody><tr><td style='text-align: center;'>foo</td><td style='text-align: center;'>bar</td></tr><tr><td>foo<br>bar</td><td>foo<br>bar</td></tr><tr><td><u>foo</u><br><u>bar</u></td><td><u>foo</u><br><b>bar</b></td></tr></tbody></table>""",  # noqa: E501
            """<table border="1" style="border-collapse: collapse;">\n  <caption>foobar</caption>\n  <colgroup>\n    <col style="width: 20%;">\n    <col style="width: 80%;">\n  </colgroup>\n  <tbody>\n    <tr>\n      <td style="text-align: center;">foo</td>\n      <td style="text-align: center;">bar</td>\n    </tr>\n    <tr>\n      <td>foo<br>bar</td>\n      <td>foo<br>bar</td>\n    </tr>\n    <tr>\n      <td><u>foo</u><br><u>bar</u></td>\n      <td><u>foo</u><br><b>bar</b></td>\n    </tr>\n  </tbody>\n</table>""",  # noqa: E501
        ),
        (
            """<td style="foo: bar">foobar</td>""",
            """<td>foobar</td>""",
        ),
    ),
)
def test_html_formatter(input: str, expected_output: str) -> None:
    ret_1, _ = format_html(input, False)
    ret_2, _ = format_html(ret_1, False)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        (
            """<section>\n  foo<br>\n  <b>bar</b>\n</section>""",
            """<section>foo<br><b>bar</b></section>""",
        ),
    ),
)
def test_html_formatter_minimized(input: str, expected_output: str) -> None:
    ret_1, _ = format_html(input, True)
    ret_2, _ = format_html(ret_1, True)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("", ""),
        ("3.6.24", "06/2024"),
        ("3/6/24", "06/2024"),
        ("6/24", "06/2024"),
        ("3.6.2024", "06/2024"),
        ("3/6/2024", "06/2024"),
        ("6/2024", "06/2024"),
    ),
)
def test_date_formatter(input: str, expected_output: str) -> None:
    ret_1, _ = format_date(input, False)
    ret_2, _ = format_date(ret_1, False)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        ("", ""),
        ("AMBOSS", "AMBOSS"),
        ("AMBOSS, Wikipedia", "AMBOSS, Wikipedia"),
        ("Wikipedia, AMBOSS", "AMBOSS, Wikipedia"),
    ),
)
def test_source_formatter(input: str, expected_output: str) -> None:
    ret_1, _ = format_source(input, False)
    ret_2, _ = format_source(ret_1, False)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        (
            """""",
            """""",
        ),
        (
            """<div class="mt-anki-iframe-src" data-src="1709395038956"></div>""",
            """<div class="mt-anki-iframe-src" data-src="1709395038956"></div>""",
        ),
    ),
)
def test_meditricks_formatter(input: str, expected_output: str) -> None:
    ret_1, _ = format_meditricks(input, False)
    ret_2, _ = format_meditricks(ret_1, False)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        (
            """""",
            """""",
        ),
        (
            """<a href="https://de.wikipedia.org/wiki/Golgi-Apparat">foo</a>""",
            """<a href="https://de.wikipedia.org/wiki/Golgi-Apparat">Golgi-Apparat – Wikipedia</a>""",  # noqa: E501
        ),
        (
            """<a href="https://flexikon.doccheck.com/de/Endoplasmatisches_Retikulum">foo</a>""",
            """<a href="https://flexikon.doccheck.com/de/Endoplasmatisches_Retikulum">Endoplasmatisches Retikulum – DocCheck Flexikon</a>""",  # noqa: E501
        ),
        (
            """<a href="https://de.wikipedia.org/wiki/Golgi-Apparat">foo</a><a href="https://de.wikipedia.org/wiki/Golgi-Apparat">foo</a>""",  # noqa: E501
            """<a href="https://de.wikipedia.org/wiki/Golgi-Apparat">Golgi-Apparat – Wikipedia</a><br>\n<a href="https://de.wikipedia.org/wiki/Golgi-Apparat">Golgi-Apparat – Wikipedia</a>""",  # noqa: E501
        ),
    ),
)
@patch("anki_formatter.formatters.common.requests.get", side_effect=mocked_links_requests)
def test_links_formatter(mock_get: Mock, input: str, expected_output: str) -> None:
    ret_1, _ = format_links(input, False)
    ret_2, _ = format_links(ret_1, False)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


@pytest.mark.parametrize(
    ("input", "expected_output"),
    (
        (
            """""",
            """""",
        ),
        (
            """<a href="https://de.wikipedia.org/wiki/Golgi-Apparat">foo</a><a href="https://de.wikipedia.org/wiki/Golgi-Apparat">foo</a>""",  # noqa: E501
            """<a href="https://de.wikipedia.org/wiki/Golgi-Apparat">Golgi-Apparat – Wikipedia</a><br><a href="https://de.wikipedia.org/wiki/Golgi-Apparat">Golgi-Apparat – Wikipedia</a>""",  # noqa: E501
        ),
    ),
)
@patch("anki_formatter.formatters.common.requests.get", side_effect=mocked_links_requests)
def test_links_formatter_minimized(mock_get: Mock, input: str, expected_output: str) -> None:
    ret_1, _ = format_links(input, True)
    ret_2, _ = format_links(ret_1, True)

    assert ret_1 == expected_output
    assert ret_2 == expected_output


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
    <rect id='628be4152337460db5e8d5e58c13425a-ao-1' x='0' y='1364' width='261' height='135' fill='#FFEBA2' stroke='#2D2D2D' stroke-width='1'/>
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
    ret_1 = format_image_occlusion_svg(input)
    ret_2 = format_image_occlusion_svg(ret_1)

    assert ret_1 == expected_output
    assert ret_2 == expected_output
