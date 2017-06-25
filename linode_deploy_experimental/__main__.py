import argparse
import os
import string
import subprocess
import sys
import time

from linode_api3 import linode, avail, init

IMAGES = ["freebsd-11-0", "openbsd-6-0", "netbsd-7-1", "centos-7-0"]

grub_kernel_id = 210
direct_disk_kernel_id = 213


def wait_for_created(l):
    while not hasattr(l, "totalhd"):
        print("Waiting for Linode to be created")
        l = linode.view(linode_id=l.linodeid)[0]
        time.sleep(1)

    return l


def wait_for_running(l):
    while l.status != 1:
        print("Waiting for Linode to boot into install config")
        l = linode.view(l.linodeid)[0]
        time.sleep(15)

    return l


def wait_for_ssh(address, password, cmd):
    this_path = os.path.dirname(os.path.realpath(__file__))
    tcl_path = os.path.join(this_path, "ssh.tcl")
    while subprocess.call([tcl_path, address, password, cmd]) > 0:
        print("Waiting for ssh server")
        time.sleep(15)


def generate_tmp_password():
    # Better than nothing? http://stackoverflow.com/a/13901912/1507139
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
    password = ''
    for i in range(60):
        password += chars[ord(os.urandom(1)) % len(chars)]
    return password


def get_args():
    parser = argparse.ArgumentParser()

    image_help = ("must supply an image. Options are [{}]"
                "").format(", ".join(IMAGES))
    parser.add_argument("image", help=image_help, type=str)

    key_help = "your APIv3 key must be supplied."
    parser.add_argument("--api_key", help=key_help, type=str,
                        default=os.environ.get("LINODE_APIV3_KEY"))

    boot_immediately_help = ("Boots immediately into the image after install "
                             "with an unsafe password")
    parser.add_argument("-b", "--boot-immediately",
                        help=boot_immediately_help, action="store_true")

    no_cleanup_help = "Prevent temporary disks and configs from being deleted"
    parser.add_argument("-n", "--no-cleanup",
                        help=no_cleanup_help, action="store_true")

    delete_on_failure_help = "Automatically deletes the created Linode on script failure"
    parser.add_argument("-d", "--delete-on-failure",
                        help=delete_on_failure_help, action="store_true")

    args = parser.parse_args()

    if not args.api_key:
        exit("LINODE_APIV3_KEY environment variable or --api_key flag must be set.")

    if not args.image in IMAGES:
        exit("image must be one of [{}]".format(", ".join(IMAGES)))

    return args


def main():
    args = get_args()

    init(args.api_key)

    datacenters = avail.datacenters()
    print("Fetched all datacenters")
    fremont = [d for d in datacenters if "fremont" in d.location.lower()][0]

    distributions = avail.distributions()
    print("Fetched all distributions")
    debian = [d for d in distributions if "debian" in d.label.lower()][0]

    plans = avail.linodeplans()
    print("Fetched all plans")
    # TODO: make this selectable
    smallest_plan = sorted(plans, key=lambda p: p.ram)[0]

    tmp_password = generate_tmp_password()

    try:
        l = linode.create(fremont.datacenterid, smallest_plan.planid)
        print("Created a linode")

        l = wait_for_created(l)

        linode.ip.addprivate(l.linodeid)
        print("Added private IP")

        tmp_disk_size = 1024
        main_disk_size = l.totalhd - tmp_disk_size
        primary_disk = linode.disk.create(l.linodeid, "PrimaryDisk", "raw", main_disk_size)
        print("Created first disk")

        tmp_disk = linode.disk.create_from_distribution(
            l.linodeid, debian.distributionid, "TemporaryDisk", tmp_disk_size, tmp_password)
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
            time.sleep(5)

        no_helpers = {
            "disable_update_db": False,
            "distro": False,
            "xen": False,
            "depmod": False,
            "network": False,
        }

        install_config_helpers = no_helpers.copy()
        install_config_helpers["network"] = True
        install_config = linode.config.create(
            l.linodeid, grub_kernel_id, "Install Config",
            [tmp_disk.diskid, primary_disk.diskid], helpers=install_config_helpers)
        print("Created install config")

        normal_config = linode.config.create(
            l.linodeid, direct_disk_kernel_id, "Normal Config", [primary_disk.diskid],
            helpers=no_helpers)
        print("Created normal config")

        linode.boot(l.linodeid, install_config.configid)
        l = wait_for_running(l)

        # Allow time for ssh server to start
        print("Waiting for ssh server to start")
        time.sleep(30)

        ips = linode.ip.view(l.linodeid)
        print("Fetched ips")
        ip = [ip for ip in ips if ip.ispublic][0]

        print("Started image deploy process")
        cmd = ("curl ftp://192.168.143.223/{}.img.gz | "
               "gunzip -c | "
               "dd of=/dev/sdb").format(args.image)
        wait_for_ssh(ip.ipaddress, tmp_password, cmd)

        print("Image deployed")

        if not args.no_cleanup:
            print("Shutting down for cleanup")
            linode.shutdown(l.linodeid)
            print("Cleaning up temporary configs and disks")
            linode.config.delete(l.linodeid, install_config.configid)
            linode.disk.delete(l.linodeid, tmp_disk.diskid)

            # Resize primary disk to full size
            linode.disk.resize(l.linodeid, primary_disk.diskid, l.totalhd)

        if args.boot_immediately:
            print("Linode rebooting")
            linode.reboot(l.linodeid, normal_config.configid)

        status = "powering off"
        if args.boot_immediately:
            status = "booting into {} and will be ready shortly".format(args.image)
            print(("Your Linode is {}.\n\n"
                   "Id: {}\n"
                   "IP Address: {}\n"
                   "User: root\n"
                   "Password: password123\n\n"
                   "Root access over SSH is disabled.").format(
                       status, l.linodeid, ip.ipaddress))
    except Exception as e:
        print("Oh no! An exception!")
        if args.delete_on_failure and hasattr(l, "linodeid") and l.linodeid:
            print("Deleting Linode")
            linode.delete(l, skip_checks=True)
        raise e


if __name__ == "__main__":
    main()
