#!/usr/bin/env python2
from __future__ import print_function

import os
import sys

import pyudev
import yaml

sys.path.append(os.getenv("HOME") + "/.sr/tools/python")
sys.path.append(os.getenv("HOME") + "/.sr/tools/python/inventory")

import inventory.query


def get_device(path):
    context = pyudev.Context()
    return pyudev.Device.from_device_file(context, path)


def replace_serial_line(path, new_serial):
    lines = []

    with open(path) as fd:
        for line in fd:
            lines.append(line)

    for i, line in enumerate(lines):
        if line.startswith("serial:"):
            lines[i] = "serial: '{}'\n".format(new_serial)
            break
    else:
        lines.append("serial: '{}'\n".format(new_serial))

    with open(path, "w") as fd:
        fd.write("".join(lines))


def update_device_serial(new_serial):
    while True:
        code = raw_input("Asset code: ")
        result = inventory.query.query("code:{}".format(code), inv=inv.root)
        if result:
            item = result[0]
            replace_serial_line(item.path, new_serial)
        else:
            print("COULD NOT FIND THE DEVICE!")


def test_device(device, inv):
    print("=" * 80)
    serial_number = device["ID_SERIAL_SHORT"]
    result = inventory.query.query("serial:{}".format(serial_number), inv=inv.root)
    if result:
        item = result[0]
        print(item.description)
        print("Asset code: {item.code}".format(item=item))
        print()
        yes = raw_input("Is this correct? [Y/n] ")
        if yes.lower() == "n":
            replace_serial_line(item.path, "")
            update_device_serial(serial_number)
    else:
        update_device_serial(serial_number)


if __name__ == "__main__":
    device = get_device(sys.argv[1])
    inv = inventory.Inventory(sys.argv[2])
    test_device(device, inv)
