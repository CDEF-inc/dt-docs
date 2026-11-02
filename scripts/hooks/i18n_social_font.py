# This file is part of Dependency-Track.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) OWASP Foundation. All Rights Reserved.

"""Render social cards of Japanese pages legibly.

The site-wide card font has no Japanese glyphs, so Japanese titles would render
as boxes. The social plugin lets a page override `cards_layout_options` in its
`social` metadata, which this hook sets for pages that mkdocs-static-i18n marks
as Japanese. It runs before the social plugin renders the card.

The social plugin also breaks title lines only at whitespace, and Japanese has
none between words, so a long title would overflow the card. The hook inserts a
space wherever a line has to break, measured with the card font. The plugin
then breaks lines at exactly those spaces.
"""

import logging
import re
from statistics import stdev

from mkdocs.exceptions import PluginError
from PIL import Image, ImageDraw, ImageFont

FONT_FAMILIES = {"ja": "Noto Sans JP"}

# Title layer of the default card layout of mkdocs-material.
TITLE_WIDTH = 832
TITLE_HEIGHT = 310
TITLE_LINES = 3
TITLE_LINE_HEIGHT = 1.25
TITLE_FONT_STYLE = "Bold"

# Characters that must not start a line.
NO_LINE_START = set(
    "、。，．・：；！？ー）」』】〕ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ"
)

# Particles after which a line can break between phrases.
PARTICLES = set("のをにでとへがはも")

log = logging.getLogger("mkdocs.hooks.i18n_social_font")


def on_page_markdown(markdown, *, page, config, files):
    family = FONT_FAMILIES.get(getattr(page.file, "locale", None))
    if not family:
        return markdown

    layout = page.meta.setdefault("social", {}).setdefault("cards_layout_options", {})
    layout.setdefault("font_family", family)

    title = page.meta.get("title") or _first_heading(markdown)
    font = _title_font(config, layout["font_family"])
    if title and font and "title" not in layout:
        wrapped = _wrap(title, font)
        if wrapped != title:
            layout["title"] = wrapped
    return markdown


def _first_heading(markdown):
    match = re.search(r"^# (.+?)\s*$", markdown, re.MULTILINE)
    return match.group(1) if match else None


def _title_font(config, family):
    social = config.plugins.get("material/social")
    if social is None:
        return None
    try:
        path = social._resolve_font(family, TITLE_FONT_STYLE)
    except (OSError, PluginError) as e:
        log.warning(f"Couldn't load font '{family}' to wrap card titles: {e}")
        return None

    # Same font size computation as the social plugin.
    font = ImageFont.truetype(path, 1000)
    ascender, descender = font.getmetrics()
    extent = TITLE_LINES * ascender + descender
    extent += (TITLE_LINES - 1) * (TITLE_LINE_HEIGHT - 1) * ascender
    return ImageFont.truetype(path, int(1000 * TITLE_HEIGHT / extent))


def _wrap(title, font):
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

    def width(text):
        return draw.textlength(text, font=font)

    if all(width(word) <= TITLE_WIDTH for word in title.split()):
        return title

    # Pick the breaks that read most naturally, then the fewest and most even
    # lines, among those that the social plugin lays out without overflowing.
    best, best_key = title, None
    for lines, penalty in _candidates(title, width):
        text = " ".join(lines)
        if not all(width(line) <= TITLE_WIDTH for line in _plugin_lines(text, width)):
            continue
        key = (penalty, len(lines), max(width(line) for line in lines))
        if best_key is None or key < best_key:
            best, best_key = text, key
    return best


def _candidates(text, width, lines=1):
    if width(text) <= TITLE_WIDTH:
        yield [text], 0
    if lines == TITLE_LINES:
        return
    for i in range(1, len(text)):
        head, tail = text[:i].strip(), text[i:].strip()
        if not head or not tail or width(head) > TITLE_WIDTH:
            continue
        if tail[0] in NO_LINE_START:
            continue
        penalty = _break_penalty(text[i - 1], text[i])
        for rest, rest_penalty in _candidates(tail, width, lines + 1):
            yield [head, *rest], penalty + rest_penalty


def _break_penalty(before, after):
    if before == " " or after == " ":
        return 0
    if before in PARTICLES and _script(after) != "hiragana":
        return 0
    if _script(before) != _script(after):
        return 1
    return 3


def _script(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿":
        return "kanji"
    return "other"


def _plugin_lines(text, width):
    # Same line breaking as the social plugin: fill lines word by word, then
    # move the last word of the first of two lines down if that balances them.
    words = re.split(r"\s+", text)
    lines = [[]]
    for word in words:
        if lines[-1] and width(" ".join([*lines[-1], word])) > TITLE_WIDTH:
            lines.append([])
        lines[-1].append(word)
    if len(lines) == 2:
        first, second = lines
        a = [len(" ".join(first)), len(" ".join(second))]
        b = [len(" ".join(first[:-1])), len(" ".join([first[-1], *second]))]
        if stdev(b) < stdev(a):
            lines = [first[:-1], [first[-1], *second]]
    return [" ".join(line) for line in lines]
