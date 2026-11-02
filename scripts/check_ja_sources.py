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

"""Find Japanese pages whose English source changed since translation.

The manifest records, for each English page with a `*.ja.md` translation, the
git blob id of the English page the translation is based on. A page is
outdated when the English page no longer has that blob id. The blob id is
computed from the file content with LF line endings, so it matches the id git
stores, and `git diff <old> <new>` shows what changed in English.

Run with `--update` after updating a translation to record the current English
page as its source.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

MANIFEST = Path("i18n/ja-sources.json")


def blob_id(path: Path) -> str:
    content = path.read_bytes().replace(b"\r\n", b"\n")
    header = f"blob {len(content)}\0".encode()
    return hashlib.sha1(header + content).hexdigest()


def source_of(ja_file: Path) -> Path:
    return ja_file.with_name(ja_file.name.removesuffix(".ja.md") + ".md")


def load_manifest() -> dict[str, str]:
    if not MANIFEST.exists():
        return {}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(manifest: dict[str, str]):
    MANIFEST.parent.mkdir(exist_ok=True)
    text = json.dumps(dict(sorted(manifest.items())), indent=2, ensure_ascii=False)
    MANIFEST.write_text(text + "\n", encoding="utf-8", newline="\n")


def update(docs_dir: Path, files: list[Path]):
    manifest = load_manifest()
    targets = files or sorted(docs_dir.rglob("*.ja.md"))
    for path in targets:
        ja_file = path if path.name.endswith(".ja.md") else path.with_suffix(".ja.md")
        source = source_of(ja_file)
        if not ja_file.exists() or not source.exists():
            sys.exit(f"{ja_file}: translation or English page not found")
        manifest[source.as_posix()] = blob_id(source)
    if not files:
        current = {source_of(f).as_posix() for f in targets}
        manifest = {k: v for k, v in manifest.items() if k in current}
    save_manifest(manifest)
    print(f"Recorded the English source of {len(targets)} Japanese page(s).")


def check(docs_dir: Path) -> list[tuple[Path, str]]:
    manifest = load_manifest()
    problems = []
    for ja_file in sorted(docs_dir.rglob("*.ja.md")):
        source = source_of(ja_file)
        recorded = manifest.get(source.as_posix())
        update_hint = f"`make update-ja-sources FILES={ja_file.as_posix()}`"
        if not source.exists():
            message = f"English page {source.as_posix()} no longer exists."
        elif recorded is None:
            message = f"No recorded English source. Run {update_hint}."
        elif recorded != blob_id(source):
            diff = f"`git diff {recorded[:12]} {blob_id(source)[:12]}`"
            message = (
                f"{source.as_posix()} changed since translation. See {diff}, "
                f"update the translation, then run {update_hint}."
            )
        else:
            continue
        problems.append((ja_file, message))
    return problems


def report(problems: list[tuple[Path, str]]):
    in_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    for path, message in problems:
        if in_actions:
            print(
                f"::warning file={path.as_posix()},title=Outdated translation::{message}"
            )
        else:
            print(f"{path.as_posix()}: {message}")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and problems:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### {len(problems)} Japanese page(s) need attention\n\n")
            f.writelines(
                f"- `{path.as_posix()}`: {message}\n" for path, message in problems
            )

    if not problems:
        print("All Japanese pages match their recorded English source.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument(
        "--update",
        nargs="*",
        type=Path,
        metavar="FILE",
        help="record the current English source of these pages (all if none)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit with an error if any page is outdated",
    )
    args = parser.parse_args()

    if args.update is not None:
        update(args.docs_dir, args.update)
        return

    problems = check(args.docs_dir)
    report(problems)
    if problems and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
