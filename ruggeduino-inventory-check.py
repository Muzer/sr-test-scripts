#!/usr/bin/env python3
import os

import pyudev
import yaml


def find_ruggeduinos():
    context = pyudev.Context()
    return context.list_devices(subsystem="usb", ID_MODEL="Ruggeduino")


def find_in_inventory(serial_number, inventory):
    for dirpath, dirnames, filenames in os.walk(inventory):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            with open(path) as fd:
                try:
                    contents = fd.read()
                    if "serial" in contents:
                        try:
                            item = yaml.safe_load(contents)
                            if str(item["serial"]) == str(serial_number):
                                return dirpath
                        except (KeyError, TypeError, yaml.scanner.ScannerError):
                            pass
                except UnicodeDecodeError:
                    pass


def test_ruggeduino(device, inventory_dir):
    print("=" * 80)
    serial_number = device["ID_SERIAL_SHORT"]
    assembly_path = find_in_inventory(serial_number, inventory_dir)
    for filename in os.listdir(assembly_path):
        if filename == "info":
            continue

        print("-" * 80)

        path = os.path.join(assembly_path, filename)
        with open(path) as fd:
            item = yaml.safe_load(fd)
        print(item["description"])
        print("Asset code: {item[assetcode]}".format(item=item))
        print()
        yes = input("Is this correct? [Y/n] ")
        if yes.lower() == "n":
            item["serial"] = serial_number
            with open(path, "w") as fd:
                yaml.dump(item, fd, default_flow_style=False)


if __name__ == "__main__":
    for device in find_ruggeduinos():
        test_ruggeduino(device, "../../inventory")
