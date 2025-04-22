from __future__ import annotations


def clear(value: str, minimized: bool) -> tuple[str, bool]:
    return "", value != ""
