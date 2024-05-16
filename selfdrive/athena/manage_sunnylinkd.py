#!/usr/bin/env python3
from selfdrive.athena.manage_athenad import manage_athenad

if __name__ == '__main__':
  manage_athenad("SunnylinkDongleId", "SunnylinkdPid", 'sunnylinkd', 'selfdrive.athena.sunnylinkd')
