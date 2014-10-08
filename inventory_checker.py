#!/usr/bin/env python2
from __future__ import print_function

import re
import os
import sys
import argparse

import pyudev
import yaml

sys.path.append(os.getenv("HOME") + "/.sr/tools/python")
sys.path.append(os.getenv("HOME") + "/.sr/tools/python/inventory")

import inventory.query
from yaml_replace import *

def get_device(path):
    context = pyudev.Context()
    return pyudev.Device.from_device_file(context, path)


def update_device(new_serial, new_condition, inv):
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


def test_device(device, inv_directory, condition):
    print("=" * 80)
    serial_number = device["ID_SERIAL_SHORT"]
    inv = inventory.Inventory(inv_directory)
    result = inventory.query.query("serial:{}".format(serial_number),
                                   inv=inv.root)
    if result:
        item = result[0]
        print(item.description)
        print("Asset code: {item.code}".format(item=item))
        print()
        yes = raw_input("Is this correct? [Y/n] ")
        if yes.lower() == "n":
            replace_serial(item.path, "")
            update_device(serial_number, condition, inv)
        else:
            replace_condition(item.path, condition)
    else:
        update_device(serial_number, condition, inv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('device_path', type=str)
    parser.add_argument('inventory_directory', type=str)
    parser.add_argument('condition', type=str)
    args = parser.parse_args()

    device = get_device(args.device_path)
    test_device(args.device, args.inventory_directory, args.condition)
