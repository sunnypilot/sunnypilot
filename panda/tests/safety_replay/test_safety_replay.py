#!/usr/bin/env python3
import os
import requests

from panda import Panda
from panda.tests.safety_replay.replay_drive import replay_drive
from tools.lib.logreader import LogReader  # pylint: disable=import-error

BASE_URL = "https://commadataci.blob.core.windows.net/openpilotci/"

logs = [
  # (route, safety mode, param)
  ("2425568437959f9d|2019-12-22--16-24-37.bz2", Panda.SAFETY_HONDA_NIDEC, 0),          # HONDA.CIVIC (fcw presents: 0x1FA blocked as expected)
  ("38bfd238edecbcd7|2019-06-07--10-15-25.bz2", Panda.SAFETY_TOYOTA, 66),              # TOYOTA.PRIUS
  ("f89c604cf653e2bf|2018-09-29--13-46-50.bz2", Panda.SAFETY_GM, 0),                   # GM.VOLT
  ("6fb4948a7ebe670e|2019-11-12--00-35-53.bz2", Panda.SAFETY_CHRYSLER, 0),             # CHRYSLER.PACIFICA_2018_HYBRID
  ("791340bc01ed993d|2019-04-08--10-26-00.bz2", Panda.SAFETY_SUBARU, 0),               # SUBARU.IMPREZA
  ("76b83eb0245de90e|2020-03-05--19-16-05.bz2", Panda.SAFETY_VOLKSWAGEN_MQB, 0),       # VOLKSWAGEN.GOLF (MK7)
  ("d12cd943127f267b|2020-03-27--15-57-18.bz2", Panda.SAFETY_VOLKSWAGEN_PQ, 0),        # 2009 VW Passat R36 (B6), supporting OP port not yet upstreamed
  ("fbbfa6af821552b9|2020-03-03--08-09-43.bz2", Panda.SAFETY_NISSAN, 0),               # NISSAN.XTRAIL
  ("5b7c365c50084530_2020-04-15--16-13-24--3--rlog.bz2", Panda.SAFETY_HYUNDAI, 0),     # HYUNDAI.SONATA
  ("610ebb9faaad6b43|2020-06-13--15-28-36.bz2", Panda.SAFETY_HYUNDAI_LEGACY, 0),       # HYUNDAI.IONIQ_EV_LTD
  ("5ab784f361e19b78_2020-06-08--16-30-41.bz2", Panda.SAFETY_SUBARU_LEGACY, 0),        # SUBARU.OUTBACK
  #("e19eb5d5353b1ac1|2020-08-09--14-37-56.bz2", Panda.SAFETY_SUBARU_LEGACY, 1),       # SUBARU.OUTBACK_PREGLOBAL_2018
  ("bb50caf5f0945ab1|2021-06-19--17-20-18.bz2", Panda.SAFETY_TESLA, 0),                # TESLA.AP2_MODELS
  ("bd6a637565e91581_2021-10-29--22-18-31--1--rlog.bz2", Panda.SAFETY_MAZDA, 0),       # MAZDA.CX9_2021
]


if __name__ == "__main__":

  # get all the routes
  for route, _, _ in logs:
    if not os.path.isfile(route):
      with open(route, "wb") as f:
        f.write(requests.get(BASE_URL + route).content)

  failed = []
  for route, mode, param in logs:
    lr = LogReader(route)

    print("\nreplaying %s with safety mode %d and param %s" % (route, mode, param))
    if not replay_drive(lr, mode, int(param)):
      failed.append(route)

    for f in failed:  # type: ignore
      print(f"\n**** failed on {f} ****")
    assert len(failed) == 0, "\nfailed on %d logs" % len(failed)
