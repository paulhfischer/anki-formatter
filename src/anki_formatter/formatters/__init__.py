from __future__ import annotations

from anki_formatter.formatters.clear import clear
from anki_formatter.formatters.date import format_date
from anki_formatter.formatters.html import format_html
from anki_formatter.formatters.image_occlusion_svg import format_image_occlusion_field
from anki_formatter.formatters.occlusion import format_occlusion
from anki_formatter.formatters.plaintext import convert_to_plaintext
from anki_formatter.formatters.skip import skip
from anki_formatter.formatters.source import format_source

FORMATTERS = {
    "clear": clear,
    "plaintext": convert_to_plaintext,
    "html": format_html,
    "skip": skip,
    "occlusion": format_occlusion,
    "imageOcclusionSVG": format_image_occlusion_field,
    "source": format_source,
    "date": format_date,
}
