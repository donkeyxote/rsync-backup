#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from settings import DISKS, FORCE_CLEAN, LOGLEVEL
from disk import Disk


def select_disk():
    disks = []
    for name, path in DISKS:
        try:
            disks.append(Disk(mount_point=path))
        except FileNotFoundError:
            print("{} is not a valid path for {}: skipping...".format(path, name))
    try:
        selected_disk = sorted(disks)[0]
        if LOGLEVEL > 0:
            print("Backup scheduled on disk at {}".format(selected_disk.mount_point))
        return selected_disk
    except IndexError:
        print("No disks available: aborting.")
        exit(1)
    return None


if __name__ == "__main__":
    disk = select_disk()
    if FORCE_CLEAN is True or not disk.has_space():
        disk.free_space(force_clean=FORCE_CLEAN)
    disk.do_backup()
