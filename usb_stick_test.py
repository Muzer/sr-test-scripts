#!/usr/bin/env python2
from __future__ import print_function

import os
import pyudev
import subprocess
import sys
import tempfile

import inventory_checker


def find_usb_sticks():
    context = pyudev.Context()
    for device in context.list_devices(DEVTYPE="disk"):
        if device["MAJOR"] == "8" and device["ID_BUS"] == "usb":
            yield device


def test_device(device):
    try:
        subprocess.check_call(["sudo", "echo", "-n"]) # to make sure sudo password is in cache

        print("Creating partition table.")
        process = subprocess.Popen(["sudo", "fdisk", device["DEVNAME"]], stdout=subprocess.PIPE,
                                                                         stderr=subprocess.PIPE,
                                                                         stdin=subprocess.PIPE)
        stdout, stderr = process.communicate(input="o\nn\n\n\n\n\nw\n")

        print("Formatting partition as FAT.")
        subprocess.check_call(["sudo", "mkfs.vfat", device["DEVNAME"] + "1"])

        print("Creating '.srobo' file.")
        mount_dir = tempfile.mkdtemp()
        subprocess.check_call(["sudo", "mount", device["DEVNAME"] + "1", mount_dir])
        subprocess.check_call(["sudo", "touch", mount_dir + "/.srobo"])
        subprocess.check_call(["sync"])
        subprocess.check_call(["sudo", "umount", mount_dir])
        os.rmdir(mount_dir)

        return True
    except Exception as e:
        print(e)
        return False

    # write .srobo file


def run_tests(inventory_dir):
    usb_sticks = list(find_usb_sticks())
    print("Running tests on: {}".format([device["DEVNAME"] for device in usb_sticks]))
    raw_input("Confirm? ")
    for usb_stick in usb_sticks:
        print("Testing {} ({}).".format(usb_stick["ID_MODEL"], usb_stick["DEVNAME"]))
        working = test_device(usb_stick)
        condition = "working" if working else "not working"
        print("{} is {}.".format(usb_stick["ID_MODEL"], condition))
        inventory_checker.test_device(usb_stick, inventory_dir, condition)


if __name__ == "__main__":
    while True:
        run_tests(sys.argv[1])
        raw_input("Press return to move to the next USB sticks.")
