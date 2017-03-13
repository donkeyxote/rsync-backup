#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import datetime
import os

BASE_DIR = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
TODAY = datetime.date.today()

if os.path.isfile('/etc/rsync-backup.conf'):
    config_file = '/etc/rsync-backup.conf'
elif os.path.isfile(os.path.join(BASE_DIR, 'config.ini')):
    config_file = 'config.ini'
else:
    config_file = None
    exit(1)

config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, config_file))

rule_sections = (name for name in config.sections() if name.startswith('rule'))
RULES = []
for rule in rule_sections:
    RULES.append({'after': datetime.timedelta(days=config.getint(rule, 'after')),
                  'keep_one_every': datetime.timedelta(days=config.getint(rule, 'keep_one_every'))})

RULES = sorted(RULES, key=lambda k: k['after'])

BACKUP_SRC = config.get('paths', 'backup_src')
BACKUP_TMP = config.get('paths', 'backup_tmp')

TIME_FORMAT = config.get('paths', 'time_format', fallback='%Y-%m-%d')

MAX_BLOCKS_PERCENT_USAGE = config.getint('limits', 'max_blocks_percent_usage', fallback=50)
MAX_INODES_PERCENT_USAGE = config.getint('limits', 'max_inodes_percent_usage', fallback=50)

DISKS = config.items(section='disks')

FORCE_CLEAN = config.getboolean('misc', 'force_clean', fallback=False)

COMMAND = config.get('misc', 'command', fallback='rsync -av --delete')

LOGLEVEL = config.getint('misc', 'loglevel', fallback=0)

COPY_COMMAND = config.get('misc', 'copy_command', fallback='cp -afluv -T')

DELETE_COMMAND = config.get('misc', 'delete_command', fallback='rsync -av --delete')

KEEP_DELETED = config.getboolean('misc', 'keep_deleted', fallback=False)
