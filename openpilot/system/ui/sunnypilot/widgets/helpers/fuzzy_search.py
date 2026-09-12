"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import re
import unicodedata


def normalize(text: str) -> str:
  return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()


def search_from_list(query: str, items: list[str]) -> list[str]:
  if not query:
    return items

  normalized_query = normalize(query)
  search_terms = [re.sub(r'[^a-z0-9]', '', term) for term in normalized_query.split() if term.strip()]

  results = []
  for item in items:
    normalized_item = normalize(item)
    item_with_spaces = re.sub(r'[^a-z0-9\s]', ' ', normalized_item)
    item_stripped = re.sub(r'[^a-z0-9]', '', normalized_item)

    all_terms_match = True
    for term in search_terms:
      if not term:
        continue

      if term not in item_with_spaces and term not in item_stripped:
        all_terms_match = False
        break

    if all_terms_match:
      results.append(item)

  return results
