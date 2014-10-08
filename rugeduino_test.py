#!/usr/bin/env python2
# usage rugiduino-test /dev/ttyACM0 ../inventory

from rugeduino_test_lib import *
from inventory_checker import *
import os

if __name__=="__main__":
	print "Reprogramming board (if an arduino window apears then this needs to be done manualy)"
	os.system("arduino --upload ruggeduino-fw.ino")


	print "testing"
	if runtest():
		print "All tests completed successfully"
		condition = "working" 
	else:
		print "broken board"
		condition = "broken"
	print "inventorizing"

	device_path = sys.argv[1]
	inventory_directory = sys.argv[2]
	device = get_device(device_path)
	test_device(device, inventory_directory, condition)
