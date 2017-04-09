#!/usr/bin/expect -f

set timeout 120

set ip    [lindex $argv 0]
set pw    [lindex $argv 1]
set cmd   [lindex $argv 2]

spawn ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "root@$ip" "$cmd"
expect "assword:"
send "$pw\r"
interact
