#!/usr/bin/env python3

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

"""Give headings in Japanese pages the same ids as the English pages.

The default slugify drops Japanese characters, so a translated heading would
lose the anchor that links point to. This script reads the heading ids from the
built English site and writes them to the matching h2-h6 headings of each
`*.ja.md` file as `{#id}`, the form markdownlint also recognizes. Run
`make build` first.
"""

import argparse
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^(#{2,6}) (.*?)(?: \{ ?#([^ }]+) ?\})?\s*$")
H_TAG = re.compile(r'<h([2-6]) id="([^"]+)"')


def english_heading_ids(site_dir: Path, rel: str) -> list[tuple[int, str]]:
    page_dir = rel.removesuffix("index") if rel.endswith("index") else rel
    html = (site_dir / page_dir / "index.html").read_text(encoding="utf-8")
    article = html.split('<article class="md-content__inner', 1)[1].split(
        "</article>", 1
    )[0]
    return [(int(level), heading_id) for level, heading_id in H_TAG.findall(article)]


def heading_lines(lines: list[str]) -> list[int]:
    result = []
    in_fence = False
    for n, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and HEADING.match(line):
            result.append(n)
    return result


def sync(ja_file: Path, docs_dir: Path, site_dir: Path, check: bool) -> bool:
    rel = ja_file.relative_to(docs_dir).as_posix().removesuffix(".ja.md")
    english = english_heading_ids(site_dir, rel)
    lines = ja_file.read_text(encoding="utf-8").split("\n")
    indexes = heading_lines(lines)

    if len(indexes) != len(english):
        print(f"{ja_file}: {len(indexes)} headings, English page has {len(english)}")
        return False

    ok = True
    for n, (level, heading_id) in zip(indexes, english):
        match = HEADING.match(lines[n])
        if len(match.group(1)) != level:
            print(f"{ja_file}:{n + 1}: heading level differs from the English page")
            ok = False
            continue
        updated = f"{match.group(1)} {match.group(2)} {{#{heading_id}}}"
        if updated != lines[n]:
            if check:
                print(f"{ja_file}:{n + 1}: expected id #{heading_id}")
                ok = False
            lines[n] = updated

    if ok and not check:
        ja_file.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument("--site-dir", type=Path, default=Path("site"))
    parser.add_argument(
        "--check",
        action="store_true",
        help="report missing or wrong ids without writing",
    )
    args = parser.parse_args()

    results = [
        sync(f, args.docs_dir, args.site_dir, args.check)
        for f in sorted(args.docs_dir.rglob("*.ja.md"))
    ]
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
