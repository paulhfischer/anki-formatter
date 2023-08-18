from __future__ import annotations

import sys

if "pytest" not in sys.modules:
    from anki.hooks import addHook
    from aqt.browser import Browser

    from anki_formatter.main import main

    def setup_menu(browser: Browser) -> None:
        format_action = browser.form.menuEdit.addAction("Format Notes")
        format_action.triggered.connect(lambda _, b=browser: main(b))

    addHook("browser.setupMenus", setup_menu)
