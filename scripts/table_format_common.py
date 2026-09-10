"""Shared typography and per-cell, line-aware data-table alignment."""
import os
import unicodedata
import warnings
from functools import lru_cache
from pathlib import Path

BLUE = "2F75B5"
HEADER_FILL = "005D8D"
SECTION_FILL = "DCE6F1"
NOTE_FILL = "EEF5F8"
DEFAULT_FONT = "Microsoft YaHei"
LOCAL_SIZE = 10.5
NATIVE_SIZE = 10
TABLE_ALIGNMENT = "center"


def color_key(value):
    return str(value or "").lstrip("#").upper()


def column_alignment(header, values):
    """Legacy single-line default; generators must decide alignment per cell."""
    return TABLE_ALIGNMENT


@lru_cache(maxsize=32)
def measurement_font(font, bold):
    """Use actual glyph advances when available, without installing fonts."""
    try:
        from PIL import ImageFont
        candidates = [font]
        if font.casefold() in {"microsoft yahei", "微软雅黑"}:
            candidates.insert(0, str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
                                     / ("msyhbd.ttc" if bold else "msyh.ttc")))
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size=100)
            except OSError:
                continue
    except ImportError:
        pass
    warnings.warn(f"No glyph metrics for {font!r}; wrap estimates require rendered review.", RuntimeWarning)
    return None


def cell_alignment(paragraphs, width_pt=None, size_pt=LOCAL_SIZE, font=DEFAULT_FONT, bold=False):
    """Explicit lines are exact; soft wrapping is an estimate, not layout verification."""
    texts = [text for text in paragraphs if text.strip()]
    if len(texts) > 1 or any("\n" in text or "\r" in text for text in texts):
        return "left"
    if not texts or width_pt is None:
        return TABLE_ALIGNMENT
    text = texts[0].strip().expandtabs(4)
    face = measurement_font(font, bold)
    if face is not None:
        length = face.getlength(text) * size_pt / 100
    else:
        length = sum(0 if unicodedata.combining(c) else
                     1 if unicodedata.east_asian_width(c) in {"W", "F"} else .55 for c in text) * size_pt
    return "left" if length > width_pt else TABLE_ALIGNMENT


def table_role(row_count, column_count, fills, has_nested=False, explicit=None):
    if explicit in {"data", "support", "layout"}:
        return explicit
    if column_count == 1 and has_nested:
        return "layout"
    if row_count == 1 and column_count == 1 and HEADER_FILL not in {color_key(f) for f in fills}:
        return "support"
    return "data"


def row_style(index, section=False):
    if index == 0:
        return {"bold": True, "color": "FFFFFF", "fill": HEADER_FILL}
    if section:
        return {"bold": True, "color": BLUE, "fill": SECTION_FILL}
    return {"bold": False, "color": "000000", "fill": None}
