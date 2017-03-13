#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from settings import TODAY, TIME_FORMAT, MAX_BLOCKS_PERCENT_USAGE, MAX_INODES_PERCENT_USAGE, BACKUP_TMP, BACKUP_SRC, \
    COMMAND, LOGLEVEL, COPY_COMMAND, DELETE_COMMAND, KEEP_DELETED
import os
import subprocess
import datetime
from directory import Directory


class Disk:

    def __init__(self, mount_point):
        self.mount_point = mount_point
        self.__st = os.statvfs(self.mount_point)

    def __lt__(self, other):
        last_backup = self.get_last_backup()
        other_last_backup = other.get_last_backup()
        if last_backup is None:
            if other_last_backup is not None and other_last_backup.datetime.date() == TODAY:
                return False
            elif other_last_backup is None:
                return False
            return True
        elif last_backup.datetime.date() == TODAY:
            return True
        elif other_last_backup is None:
            return False
        elif other_last_backup is not None and other_last_backup.datetime.date() == TODAY:
            return False
        else:
            return last_backup.datetime.date() < other_last_backup.datetime.date()

    def has_space(self):
        self.__st = os.statvfs(self.mount_point)
        blocks_percent_used = ((self.__st.f_blocks - self.__st.f_bavail) * 100 / self.__st.f_blocks)
        inodes_percent_used = ((self.__st.f_files - self.__st.f_favail) * 100 / self.__st.f_files)
        if (blocks_percent_used > MAX_BLOCKS_PERCENT_USAGE) or (inodes_percent_used > MAX_INODES_PERCENT_USAGE):
            return False
        else:
            return True

    def get_backup_dst(self):
        return os.path.join(self.mount_point, BACKUP_TMP)

    def get_last_backup(self):
        dirs = (x for x in
                sorted((Directory(date=x, path=self.mount_point) for x in
                       os.listdir(self.mount_point) if is_date(date=x, time_format=TIME_FORMAT)), reverse=True))
        try:
            return next(dirs)
        except StopIteration:
            return None

    def free_space(self, force_clean=False):
        if LOGLEVEL > 0:
            if force_clean is False and not self.has_space():
                print("Disk at {} has no space left:{}deleting some old backups...".format(self.mount_point,
                                                                                           os.linesep))
            elif force_clean is True:
                print("Force clean on disk {}:{}deleting all old backups...".format(self.mount_point, os.linesep))
        dirs = (x for x in
                sorted(Directory(date=x, path=self.mount_point) for x in
                       os.listdir(self.mount_point) if is_date(date=x, time_format=TIME_FORMAT)))
        try:
            previous_backup = next(dirs)
            for tmp_dir in dirs:
                if not force_clean and self.has_space():
                    break
                else:
                    if tmp_dir.is_deletable(previous_dir=previous_backup):
                        tmp_dir.remove()
                    else:
                        previous_backup = tmp_dir
        except StopIteration:
            pass
        if not self.has_space():
            if LOGLEVEL > 0:
                print("No more useless backup: deleting from the oldest")
        dirs = (x for x in
                sorted((Directory(date=x, path=self.mount_point) for x in
                        os.listdir(self.mount_point) if is_date(date=x, time_format=TIME_FORMAT))))
        while not self.has_space():
            try:
                next(dirs).remove()
            except StopIteration:
                print("All backup removed but still not enough space. Aborting.")
                exit(1)
        if LOGLEVEL > 0:
            print("Cleanup finished.")

    def do_backup(self):
        if not os.path.isdir(s=self.get_backup_dst()):
            self.create_tmp_dir()
        tmp_dir = self.get_backup_dst() + os.path.sep
        dst_dir = os.path.join(self.mount_point, TODAY.strftime(TIME_FORMAT)) + os.path.sep
        command = COMMAND.split() + [BACKUP_SRC, tmp_dir]
        copy_command = COPY_COMMAND.split() + [tmp_dir, dst_dir]
        delete_command = DELETE_COMMAND.split() + [tmp_dir, dst_dir]
        if LOGLEVEL > 0:
            print("Starting rsync now...")
            print("Executing  {}".format(' '.join(command)))
        if LOGLEVEL > 1:
            print(subprocess.check_output(command).decode("utf-8"))
        else:
            subprocess.check_output(command)
        if LOGLEVEL > 0:
            print("Executing {}".format(' '.join(copy_command)))
        if LOGLEVEL > 1:
            print(subprocess.check_output(copy_command).decode("utf-8"))
        else:
            subprocess.check_output(copy_command)
        if not KEEP_DELETED:
            if LOGLEVEL > 0:
                print("Deleting old files...")
            if LOGLEVEL > 1:
                print("Executing {}".format(' '.join(delete_command)))
                print(subprocess.check_output(delete_command).decode("utf-8"))
            else:
                subprocess.check_output(delete_command)
        if LOGLEVEL > 0:
            print("Done.")

    def create_tmp_dir(self):
        if LOGLEVEL > 0:
            print("Creating destination directory for rsync at {}".format(self.get_backup_dst()))
        last_backup = self.get_last_backup()
        if last_backup is not None:
            copy_command = COPY_COMMAND.split() + [last_backup.full_path, self.get_backup_dst()]
            subprocess.check_output(copy_command)
        else:
            os.mkdir(self.get_backup_dst())

    def create_test_dirs(self, since=2015):
        cur_date = TODAY
        while cur_date.year > since:
            try:
                os.makedirs(os.path.join(self.mount_point, cur_date.strftime(format=TIME_FORMAT)))
            except FileExistsError:
                pass
            cur_date = cur_date - datetime.timedelta(days=1)


def is_date(date, time_format=TIME_FORMAT):
    try:
        datetime.datetime.strptime(date, time_format)
        return True
    except ValueError:
        return False
