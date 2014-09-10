#!/usr/bin/env python2
from __future__ import print_function

import re
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


def replace_line(path, key, value):
    print("Replacing:", key, "->", value, "in", path)
    pattern = r"{key}( *):( *)(?:[^#\s]*)(.*)".format(key=key)

    with open(path) as fd:
        lines = list(fd)

    for i, line in enumerate(lines):
        match = re.match(pattern, line)
        if match is not None:
            lines[i] = "{key}{0}:{1}{value}{2}\n".format(*match.groups(), key=key, value=value)
            break
    else:
        lines.append("{}: {}\n".format(key, value))

    with open(path, "w") as fd:
        for line in lines:
            fd.write(line)


def replace_condition(path, new_condition):
    replace_line(path, "condition", new_condition)


def replace_serial(path, new_serial):
    replace_line(path, "serial", new_serial)


def update_device(new_serial, new_condition):
    while True:
        code = raw_input("Asset code: ")
        result = inventory.query.query("code:{}".format(code), inv=inv.root)
        if result:
            item = result[0]
            replace_serial(item.path, new_serial)
            replace_condition(item.path, new_condition)
            return
        else:
            print("COULD NOT FIND THE DEVICE!")


def test_device(device, inv, condition):
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
            replace_serial(item.path, "")
            update_device_serial(serial_number)
        else:
            replace_condition(item.path, condition)
    else:
        update_device(serial_number, condition)


if __name__ == "__main__":
    device = get_device(sys.argv[1])
    inv = inventory.Inventory(sys.argv[2])
    test_device(device, inv, sys.argv[3])
