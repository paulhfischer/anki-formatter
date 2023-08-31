from __future__ import annotations


def clear(value: str) -> tuple[str, bool]:
    return "", value != ""
