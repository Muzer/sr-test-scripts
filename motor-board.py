#!/usr/bin/env python3
import time

import serial
import serial.tools.list_ports

import subprocess

import re

import sys

from yaml_replace import replace_condition

class TestFailedException(Exception): pass
class NotFoundException(Exception): pass

def find_board():
    pattern = re.compile('SNR=(?P<code>SR[A-Z0-9]+)')
    for port_path, name, info in serial.tools.list_ports.comports():
        m = pattern.search(info)
        if m is not None:
            return port_path, m.group('code')

def flash_mcv4(port_path):
    print("Flashing firmware...")
    subprocess.check_call(['stm32flash', '-w', '../pyenv/pyenv/firmware/mcv4.bin',
                           '-v', port_path])
    print("Done.")

def connect(port_path):
    return serial.Serial(port_path, 1000000)

def set_speed(ser, motor_num, speed):
    if not -100 <= speed <= 100:
        raise ValueError

    ser.write([2 if motor_num is 0 else 3, speed + 128])

def move_and_confirm(ser, motor_num, speed):
    set_speed(ser, motor_num, speed)
    message = "Motor {} at power {}".format(motor_num, speed)
    print("Testing:",message)
    print("Is this the case? [Y/n]")
    choice = input()
    if choice not in 'yY' and choice is not '':
        raise TestFailedException(message)

def test_output(ser, motor_num):
    move_and_confirm(ser, motor_num, 50)
    move_and_confirm(ser, motor_num, 0)
    move_and_confirm(ser, motor_num, -50)
    set_speed(ser, motor_num, 0)

def mark_as(part_code, condition):
    path = subprocess.check_output(['sr inv-findpart '+part_code],
                                   cwd='../inventory', shell=True).strip()

    print("Part",part_code,"found at",path,". Marking as",condition)
    replace_condition(path, condition)

port_path, code = find_board()

print("Board",code,"is connected at",port_path)
print("Turn on the power supply.")

if not (len(sys.argv) > 1 and sys.argv[1] == '--no-flash'):
    print("Press firmware button, located near the USB connector on the side to "
          "right, and press return.")
    input()

    flash_mcv4(port_path)

print("Waiting 1.5 seconds for board to boot...")
time.sleep(1.5)

ser = connect(port_path)
print("Connected on",ser.name)

try:
    test_output(ser, 0)
    test_output(ser, 1)

    mark_as(code, 'working')

except TestFailedException as ex:
    print("Test failed:", ex)
    mark_as(code, 'broken')

except subprocess.CalledProcessError as ex:
    print("Could not find an inventory entry for part code",code)

finally:
    set_speed(ser, 0, 0)
    set_speed(ser, 1, 0)
