#!/bin/python
import serial
import time
ser=serial.Serial()	#create dummy serial port

def setpin(mode,pinid):
	if mode=="high":	
		ser.write("h"+chr(ord('a')+pinid))	#set pin high		
	if mode=="low":
		ser.write("l"+chr(ord('a')+pinid))	#set pin low	

	if mode=="input":
		ser.write("i"+chr(ord('a')+pinid))	#set as input	
	if mode=="output":
		ser.write("o"+chr(ord('a')+pinid))	#set as output	
	if mode=="input_pullup":
		ser.write("p"+chr(ord('a')+pinid))	#set as input_pullup
	ser.flush()				#flush the serial port
	ser.readline()				#clear any return from the rugiduino

'''
 reads the value on a pin

 \param pinid pin to read
'''
def readpin(pinid):
#	print "r"+chr(ord('a')+pinid)		#debug print			
	ser.write("r"+chr(ord('a')+pinid))	#send read command
	ser.flush()				#flush serial
	return ser.readline()			#read output

'''
Mapping of pin pairs on test harness
'''
pinmap = {
2:8,
3:9,
4:10,
5:11,
6:12,
7:13,
8:2,
9:3,
10:4,
11:5,
12:6,
13:7,

14:17,
15:18,
16:19,
17:14,
18:15,
19:16,
}

'''
 * Performs a test sequence on a pin
 * 
 * /param testpin pin id to test
 * /return True if all is ok otherwise False
'''
def testpin(pinid):
	teststatus=True			#set test as ok untill it fails

	#setup pins
	setpin("output",pinid);		#set pin under test as output
	setpin("high",pinid);		#and set pin high
	setpin("input",pinmap[pinid]);	#set pin pair as input
	
	if (readpin(pinmap[pinid])[0]!="h"):	#read target pin
		print "Error While testing pin: "+str(pinid)+" Pin pair read low when expecting high (stuck at low error)"	#report error
		teststatus=False		#fail test
	if (not checkremainingpins(pinid)):	#look for efects on other pins
		teststatus=False		#fail test

	setpin("low",pinid);		#set pin low

	if (readpin(pinmap[pinid])[0]!="l"):	#read target pin
		print "Error While testing pin: "+str(pinid)+" Pin pair read high when expecting low (stuck at high error)"	#report error
		teststatus=False		#fail test
	if (not checkremainingpins(pinid)):	#look for efects on other pins
		teststatus=False		#fail test

	setpin("input_pullup",pinid)		#return testpin to normal
	setpin("input_pullup",pinmap[pinid])	#return testpin pair to normal
	return teststatus
	
'''
Checks all other pins to see if tehey are pulled high

/return True if all is ok otherwise False
'''
def checkremainingpins(pinid):
	for pin in pinmap:				#check all known pins
		if (pin != pinid and pin != pinmap[pinid]):	#exclude pins under test
			if (readpin(pin)[0] == "l"):		#read pin
				print "Error while testing pin: "+str(pinid)+" other pin("+str(pin)+") unexpectedly read low"
				return False
	return(True)
			
'''
Tests an entire rugeduino
'''
def runtest(port='/dev/ttyACM0'):
	teststatus=True				#set test as ok untill it fails
	global ser

	ser=serial.Serial(port, 115200, timeout=1, xonxoff=0,rtscts=0)
	ser.open()

	time.sleep(2)				#wait for boot

	ser.write("v");				#check version
	ser.flush();				#flush serial
	version = ser.readline()
	if (version[0:8]=="SRduino:1"):	#check version
		print "Unexpected rugiduino version recieved: "+version	#error on incorect version
		return False

	for pin in pinmap:			#for every pin
		setpin("input_pullup",pin)	#set pin to input pullup
		

	for pin in pinmap:			# for every pin
		if not testpin(pin):		#test that pin
			tsetstatus=False	#fail the test

	ser.close()				#close serial port
	return teststatus



if __name__=="__main__":
	if runtest():
		print "All tests completed successfully"
	else:
		print "broken board"
