# rsync-backup

**rsync-backup** is a python utility to help users performing daily backup of their data.


## Key features

**rsync-backup** uses **rsync** to periodically back up some directories.

  - **Hardlinks** are used for files which haven't changed since last backup in order to keep disk usage low.
  - **Round Robin** path selection to prevent data loss in case of hardware failure.
  - **Customizable time intervals**, because you may want to delete at least some of those secular daily backups.
  - **Easy browse** as your files are accessible at any time without further operations.


## Requirements

  - python3
  - rsync


## Installation

  - Create a link to `rsbackup.py` somewhere in your $PATH.

    ```
    # ln -sf /absolute/path/to/downloaded/rsync-backup/rsbackup/rsbackup.py /usr/bin/rsync-backup
    ```

  - Move configuration file to `/etc/rsync-backup.conf`.

    ```
    # mv /path/to/downloaded/rsync-backup/config.ini /etc/rsync-backup.conf
    ```

  - Edit `/etc/rsync-backup.conf` to match your needs.

    ```
    # vim /etc/rsync-backup.conf
    ```

  - Done. You can now run rsync-backup manually, put it in your crontab or create a systemd timer.
  Make sure the user you're running `rsync-backup` with has **read permission on source** directories and **write permission on destination** directories.

    ```
    $ rsync-backup
    ```


## Configuration

  Configuration is located in file `config.ini`. It is organized in sections as follows. 


#### paths

  - **backup_src** is the path to the directory you'd like to backup.

    ```
    backup_src = /path/to/my/data/
    ```

    Mind that the **trailing /** changes the behaviour of the script the way it does with rsync.

    Check `man rsync` for further information about this.

  - **backup_tmp** is the name of the destination directory where rsync is executed.

    ```
    backup_tmp = rsync_dst
    ```

  - **time_format** is the date format used to name backup root directory. Check `man -S 3 strftime` for supported formats.

    Mind that % character must be escaped with another %.
    
    Default format is %Y-%m-%d.

    ```
    time_fotmat = %%Y%%m%%d
    ```


#### disks

  In this section you can put paths where you want to store your backups.
  The entry where last backup is the oldest will be used (Round Robin on daily base).

  You should use path on different physical devices, as it's pointless to have file backed up on different paths on the same disk (it won't protect you from hardware failure).

  ```
  [disks]
  disk1 = /path/to/my/backups/directory/on/disk1
  disk2 = /path/to/my/backups/directory/on/disk2
  disk3 = /path/to/my/backups/directory/on/disk3
  [...]
  ```

### limits

  If blocks or inodes usage grows, you will not be able to perform backup, so you have to specify at which quota some room has to be made before starting the backup. 

  - **max_blocks_percent_usage** if blocks usage is over the percentage specified, delete some old backups.

    Default is 50.

    ```
    max_blocks_percent_usage = 90
    ```

  - **max_inodes_percent_usage** if inodes usage is over the percentage specified, delete some old backups.

    Default is 50.

    ```
    max_blocks_percent_usage = 90
    ```


### rule

  Rules used to decide whether a backup is obsolete or not.

  Rule sections must start with `rule` string and has to be followed by a unique name for the rule.

  Every rule must contain 2 fields:

  - **after** is the count of days that has to pass before the rule is applied.

  - **keep_one_every** is the maximum interval of days between a backup and another.

  Default behaviour is to keep every backup.

  Here follow some examples:

  - keep a daily backup
    ```
    [rule daily]
    after = 0
    keep_one_every = 0
    ```

  - after a month keep a backup every week
    ```
    [rule weekly]
    after = 30
    keep_one_every = 7
    ```
  
  - after 6 months keep a monthly backup
    ```
    [rule monthly]
    after = 180
    keep_one_every = 30
    ```

  - after 2 years keep a backup every 6 months
    ```
    [rule 6 months]
    after = 730
    keep_one_every = 180
    ```

### misc

  Other options
  
  - **command** string to be used instead of default `rsync -av --delete`

    ```
    command = nice -n19 ionice -c2 -n7 rsync -azvH --delete
    ```

  - **force_clean** set this to `True` if you want to delete unneeded backups before disk space or inodes are required.
  
    Default is False.

    ```
    force_clean = True
    ```

  - **loglevel** is used to manage verbosity.

    Default is 0.

    - Print only warnings:
      ```
      loglevel = 0
      ```

    - Also print script output:
      ```
      loglevel = 1
      ```

    - Also print other commands output:
      ```
      loglevel = 2
      ```

  - **copy_command** string used as command to copy files between temporary backup directory and real backup directory.

    Defalut is `cp -afluv -T`.

     ```
     copy_command = cp -afluv -T
     ```

  - **delete_command** string to be used to delete old files in backup directory not present in `backup_tmp` anymore.

    Default is `rsync -av --delete`.

    ```
    delete_command = rsync -av --delete
    ```

  - **keep_deleted** set this to `True` if you want to keep files recently deleted from `backup_src` in current day backup.
    Setting this to `True` can slightly improve performances as a call to rsync is avoided.

    Default is `False`.

    ```
    keep_deleted = True
    ```
