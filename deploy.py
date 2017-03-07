import subprocess
import sys
from time import sleep

from linode_v3 import linode, avail

datacenters = avail.datacenters()
print("Fetched all datacenters")
fremont = [d for d in datacenters if "fremont" in d.location.lower()][0]

distributions = avail.distributions()
print("Fetched all distributions")
debian = [d for d in distributions if "debian" in d.label.lower()][0]

plans = avail.linodeplans()
print("Fetched all plans")
smallest_plan = sorted(plans, key=lambda p: p.ram)[0]

grub_kernel_id = 210
direct_disk_kernel_id = 213

def main():
    IMAGE = sys.argv[1]
    MAIN_PASSWORD = sys.argv[2]
    TMP_PASSWORD = sys.argv[3]

    l = linode.create(fremont.datacenterid, smallest_plan.planid)
    print("Created a linode")

    while not hasattr(l, "totalhd"):
        print("Waiting for Linode to be created")
        l = linode.view(linode_id=l.linodeid)[0]
        sleep(1)

    linode.ip.addprivate(l.linodeid)
    print("Added private IP")

    tmp_disk_size = 3072
    main_disk_size = l.totalhd - tmp_disk_size
    primary_disk = linode.disk.create_from_distribution(
        l.linodeid, debian.distributionid, "PrimaryDisk", main_disk_size, MAIN_PASSWORD)
    print("Created first disk")

    tmp_disk = linode.disk.create_from_distribution(
        l.linodeid, debian.distributionid, "TemporaryDisk", tmp_disk_size, TMP_PASSWORD)
    print("Created second disk")

    disks_to_check = [primary_disk, tmp_disk]
    i = 0
    while len(disks_to_check):
        print("Waiting for disks to be created")
        d = disks_to_check[i]
        if hasattr(d, "size"):
            del disks_to_check[i]
            print("Disk created")
        else:
            disks_to_check[i] = linode.disk.view(l.linodeid, d.diskid)[0]

        i += 1
        if i > len(disks_to_check) - 1:
            i = 0
        sleep(5)

    no_helpers = {
        "disable_update_db": False,
        "distro": False,
        "xen": False,
        "depmod": False,
        "network": False,
    }

    install_config_helpers = no_helpers.copy()
    install_config_helpers["network"] = True
    install_config =linode.config.create(
        l.linodeid, grub_kernel_id, "Install Config",
        [tmp_disk.diskid, primary_disk.diskid], helpers=install_config_helpers)
    print("Created install config")

    virt_mode = None
    if "openbsd" in IMAGE:
        virt_mode = "fullvirt"
    normal_config = linode.config.create(
        l.linodeid, direct_disk_kernel_id, "Normal Config", [primary_disk.diskid],
        helpers=no_helpers, virt_mode=virt_mode)
    print("Created normal config")

    linode.boot(l.linodeid, install_config.configid)
    while l.status != 1:
        print("Waiting for Linode to boot into install config")
        l = linode.view(l.linodeid)[0]
        sleep(15)

    # Allow time for ssh server to start
    print("Waiting for ssh server to start")
    sleep(30)

    ips = linode.ip.view(l.linodeid)
    print("Fetched ips")
    ip = [ip for ip in ips if ip.ispublic][0]

    print("Started image deploy process")
    while subprocess.call(["./ssh.tcl", IMAGE, ip.ipaddress, TMP_PASSWORD]) > 0:
        print("Waiting for ssh server")
        sleep(15)

    print("Image deployed")

    linode.reboot(l.linodeid, normal_config.configid)
    print("Rebooted into normal config")

if __name__ == "__main__":
    main()
