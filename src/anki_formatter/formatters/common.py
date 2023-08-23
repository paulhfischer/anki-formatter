from __future__ import annotations


def fix_encoding(text: str) -> str:
    return text.encode("utf-8", errors="ignore").decode("utf-8").replace("\ufeff", "")


def replace_symbols(text: str) -> str:
    return (
        text.replace("&lt;-&gt;", "↔")
        .replace("-&gt;", "→")
        .replace("&lt;-", "←")
        .replace("&lt;=&gt;", "⇔")
        .replace("=&gt;", "⇒")
        .replace("&lt;=", "⇐")
        .replace("&nbsp;", " ")
        .replace("“", '"')
        .replace("”", '"')
        .replace("„", '"')
        .replace("‟", '"')
    )
