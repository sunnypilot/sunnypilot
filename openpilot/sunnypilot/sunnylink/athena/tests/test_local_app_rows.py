from typing import cast

from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.sunnylink.athena.local_app_rows import (
  DEFAULT_APP_NAME,
  MAX_LOCAL_APP_ROWS,
  NEVER_CONNECTED,
  build_local_app_rows,
  format_age,
  short_key,
)
from openpilot.sunnypilot.sunnylink.athena.local_auth import MAX_GRANTS


def grant(app_id: str, app_name: str = "Phone") -> dict[str, str]:
  return {"app_id": app_id, "app_name": app_name, "public_key": "x", "key_id": app_id, "revision": "r"}


class TestLocalAppRows(OpenpilotTestCase):
  """The device screen's rows: one per enrolled phone."""

  def test_an_enrolled_phone_is_marked_secure(self):
    rows = build_local_app_rows([grant("key-a", "Nayan's phone")])
    self.assertEqual("Nayan's phone", rows[0].title)
    self.assertTrue(short_key("key-a") in rows[0].subtitle)
    self.assertTrue("secure" in rows[0].subtitle)

  def test_a_nameless_grant_still_gets_a_title(self):
    rows = build_local_app_rows([{"app_id": "key-a", "app_name": ""}, {"app_id": "key-b"}])
    self.assertEqual([DEFAULT_APP_NAME, DEFAULT_APP_NAME], [row.title for row in rows])

  def test_malformed_grants_are_skipped_rather_than_rendered(self):
    # The registry is JSON, so a hand-edited or older document can hold anything.
    malformed = cast(list[dict[str, str]], ["junk", {"app_name": "no id"},
                                            {"app_id": "", "app_name": "blank"}, grant("key-a")])
    rows = build_local_app_rows(malformed)
    self.assertEqual(["key-a"], [row.app_id for row in rows])

  def test_every_authorized_phone_has_a_row(self):
    """A phone the authority accepts must be visible: an invisible grant cannot be revoked."""
    rows = build_local_app_rows([grant(f"key-{i}") for i in range(MAX_GRANTS)])
    self.assertEqual(MAX_GRANTS, len(rows))
    self.assertEqual(MAX_GRANTS, MAX_LOCAL_APP_ROWS)
    self.assertEqual(MAX_LOCAL_APP_ROWS, len(build_local_app_rows([grant(f"key-{i}") for i in range(10)])))

  def test_short_key_keeps_short_ids_readable(self):
    self.assertEqual("abc", short_key("abc"))
    self.assertEqual("abcdefghij…", short_key("abcdefghijklmnop"))

  def test_a_phone_supplied_alias_wins_over_the_enrolled_name(self):
    rows = build_local_app_rows([grant("key-a", "Nayan's phone")], {"key-a": {"alias": "Garage phone"}})
    self.assertEqual("Garage phone", rows[0].title)
    # A blank or missing alias falls back to what the phone enrolled with.
    for meta in ({}, {"key-a": {}}, {"key-a": {"alias": "   "}}, {"key-a": {"alias": 7}}):
      self.assertEqual("Nayan's phone", build_local_app_rows([grant("key-a", "Nayan's phone")], meta)[0].title)

  def test_each_phone_reports_when_it_was_last_connected(self):
    rows = build_local_app_rows([grant("key-a"), grant("key-b")],
                                {"key-a": {"last_seen": 1_000.0}}, now=1_120.0)
    self.assertTrue("2m ago" in rows[0].subtitle)
    self.assertTrue(NEVER_CONNECTED in rows[1].subtitle)

  def test_a_stamp_from_before_the_last_reboot_reads_as_unknown(self):
    # Monotonic time restarts at boot, so a future-looking stamp is not "-5m ago".
    rows = build_local_app_rows([grant("key-a")], {"key-a": {"last_seen": 5_000.0}}, now=10.0)
    self.assertTrue(NEVER_CONNECTED in rows[0].subtitle)

  def test_format_age_is_coarse_and_readable(self):
    self.assertEqual("just now", format_age(0))
    self.assertEqual("just now", format_age(59.9))
    self.assertEqual("5m ago", format_age(300))
    self.assertEqual("3h ago", format_age(3 * 3600))
    self.assertEqual("2d ago", format_age(2 * 86_400))
