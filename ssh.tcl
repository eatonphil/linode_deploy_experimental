#!/usr/bin/expect -f

set timeout 120

set ip [lindex $argv 0]
set pw [lindex $argv 1]

spawn scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "deploy.sh" "root@$ip:~/"
expect "assword:"
send "$pw\r"
interact

spawn ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "root@$ip" "bash ~/deploy.sh"
expect "assword:"
send "$pw\r"
interact
