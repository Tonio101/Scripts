#!/bin/bash

# antonio@antonio101:~$ ls -lrt /etc/fail2ban/jail.d/
# -rw-r--r-- 1 root root  22 Mar 10  2022 defaults-debian.conf
# -rw-r--r-- 1 root root 104 Nov 25 21:34 sshd.conf

sudo fail2ban-client status sshd
