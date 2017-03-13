#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from settings import TODAY, TIME_FORMAT, RULES, LOGLEVEL
import datetime
import shutil
import os


class Directory:

    def __init__(self, date, path):
        self.datetime = datetime.datetime.strptime(date, TIME_FORMAT)
        self.name = date
        self.full_path = os.path.join(path, self.name)
        self.keep_one_every = datetime.timedelta(days=0)
        for rule in RULES:
            if time_passed_is_more(since=self.datetime.date(), to=TODAY, interval=rule['after']):
                self.keep_one_every = rule['keep_one_every']

    def __lt__(self, other):
        return self.datetime < other.datetime

    def is_deletable(self, previous_dir):
        return not time_passed_is_more(since=previous_dir.datetime.date(),
                                       to=self.datetime.date(), interval=self.keep_one_every)

    def remove(self):
        if LOGLEVEL > 0:
            print("Deleting directory at {}".format(self.full_path))
        shutil.rmtree(path=self.full_path)


def time_passed_is_more(since: datetime, to: datetime, interval: datetime.timedelta) -> bool:
    return to - since > interval
