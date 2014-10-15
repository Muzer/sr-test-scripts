#!/usr/bin/env python2
# usage rugiduino-test /dev/ttyACM0 ../inventory ../boards/ruggeduino-fw

from ruggeduino_test_lib import *
from inventory_checker import *
import os
import time
import sys

if __name__=="__main__":
	device_path = sys.argv[1]
	inventory_directory = sys.argv[2]
	fw_directory = sys.argv[3]
	print "Reprogramming board (trying until successful)"
	while os.system("avrdude -v -p atmega328p -c arduino -P " + device_path + " -D -U flash:w:" + os.path.join(fw_directory, "ruggeduino.hex") + ":i") != 0:
	    time.sleep(0.5)
	    print "Retrying..."

	sys.beep()
	print "Press enter to test"
	raw_input()
	print "testing"
	if runtest(device_path):
		print "All tests completed successfully"
		condition = "working" 
	else:
		print "broken board"
		condition = "broken"
	print "inventorizing"

	device = get_device(device_path)
	test_device(device, inventory_directory, condition)
