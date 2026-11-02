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

"""Make awesome-pages match localized pages against `.pages` entries.

With the suffix docs structure of mkdocs-static-i18n, a localized page such as
`index.ja.md` keeps its suffix in `src_path`. awesome-pages matches `.pages`
entries by file name, so `index.md` would not match in the localized build.
mkdocs-static-i18n stores the non-localized path in `norm_src_uri`, which this
hook makes awesome-pages use instead.
"""

from mkdocs.structure.pages import Page
from mkdocs_awesome_pages_plugin.navigation import AwesomeNavigation

_get_item_path = AwesomeNavigation._get_item_path


def _get_norm_item_path(self, item):
    if isinstance(item, Page):
        return getattr(item.file, "norm_src_uri", None) or item.file.src_path
    return _get_item_path(self, item)


AwesomeNavigation._get_item_path = _get_norm_item_path
