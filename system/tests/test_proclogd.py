from openpilot.system import proclogd


def test_smaps_refreshes_are_staggered(monkeypatch):
  monkeypatch.setattr(proclogd, "_smaps_cycle", 3)
  monkeypatch.setattr(proclogd, "_smaps_cache", {24: {"pss": 1, "pss_anon": 2, "pss_shmem": 3}})

  refreshed = {"pss": 4, "pss_anon": 5, "pss_shmem": 6}
  reads = []

  def read_smaps(pid):
    reads.append(pid)
    return refreshed

  monkeypatch.setattr(proclogd, "_read_smaps", read_smaps)

  assert proclogd._get_smaps_cached(23) == refreshed
  assert proclogd._get_smaps_cached(24) == {"pss": 1, "pss_anon": 2, "pss_shmem": 3}
  assert proclogd._get_smaps_cached(25) == {"pss": 0, "pss_anon": 0, "pss_shmem": 0}
  assert reads == [23]
