#!/bin/python
import serial
import time
ser = None


def set_pin_mode(mode, pin_id):
    if mode == "high":
        ser.write("h"+chr(ord('a')+pin_id))    #set pin high
    if mode == "low":
        ser.write("l"+chr(ord('a')+pin_id))    #set pin low

    if mode == "input":
        ser.write("i"+chr(ord('a')+pin_id))    #set as input
    if mode == "output":
        ser.write("o"+chr(ord('a')+pin_id))    #set as output
    if mode == "input_pullup":
        ser.write("p"+chr(ord('a')+pin_id))    #set as input_pullup
    ser.flush()
    ser.readline()   # clear any return from the Ruggeduino


'''
 reads the value on a pin

 \param pin_id pin to read
'''
def read_pin(pin_id):
    ser.write("r"+chr(ord('a')+pin_id))    #send read command
    ser.flush()
    return ser.readline()            #read output


'''
 reads the analogue on a pin

 \param pin_id pin to read
'''
def analogue_read_pin(pin_id):
    ser.write("a"+chr(ord('a')+pin_id))    #send read command
    ser.flush()
    return int(ser.readline())        #read output


'''
Mapping of pin pairs on test harness
'''
PIN_MAPPINGS = {
    2: 8,
    3: 9,
    4: 10,
    5: 11,
    6: 12,
    7: 13,
    8: 2,
    9: 3,
    10: 4,
    11: 5,
    12: 6,
    13: 7,

    14: 17,
    15: 18,
    16: 19,
    17: 14,
    18: 15,
    19: 16,
}

# Maps digital pin IDs (as looked-up in PIN_MAPPINGS) to analogue pin IDs
ANALOGUE_PIN_MAPPINGS = {
    14: 0,
    15: 1,
    16: 2,
    17: 3,
    18: 4,
    19: 5,
}

'''
 * Performs a test sequence on a pin
 *
 * /param pin_id pin id to test
 * /return True if all is OK otherwise False
'''
def test_pin(pin_id):
    test_passed = True

    # Set up pins
    set_pin_mode("output", pin_id)         # set pin under test as output
    set_pin_mode("high", pin_id)           # and set pin high
    set_pin_mode("input", PIN_MAPPINGS[pin_id])  # set pin pair as input

    if (read_pin(PIN_MAPPINGS[pin_id])[0] != "h"):    #read target pin
        print "Error While testing pin: "+str(pin_id)+" Pin pair read low when expecting high (stuck at low error)"    #report error
        test_passed = False        #fail test
    if (not check_remaining_pins(pin_id)):    #look for effects on other pins
        test_passed = False        #fail test
    if PIN_MAPPINGS[pin_id] in ANALOGUE_PIN_MAPPINGS:    #if analogue pin
        if analogue_read_pin(ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin_id]]) < 940:
            print "Error analogue pin ("+str(ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin_id]])+") did not read max value read:"+str(analogue_read_pin(ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin_id]]))

    set_pin_mode("low", pin_id);

    if (read_pin(PIN_MAPPINGS[pin_id])[0] != "l"):    #read target pin
        print "Error While testing pin: "+str(pin_id)+" Pin pair read high when expecting low (stuck at high error)"    #report error
        test_passed = False        #fail test
    if (not check_remaining_pins(pin_id)):    #look for effects on other pins
        test_passed = False        #fail test
    if PIN_MAPPINGS[pin_id] in ANALOGUE_PIN_MAPPINGS:    #if analogue pin
        if analogue_read_pin(ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin_id]]) > 10:
            print "Error analogue pin ("+str(ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin_id]])+") did not read min value read:"+str(analogue_read_pin(ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin_id]]))

    # Return test pins to normal
    set_pin_mode("input_pullup", pin_id)
    set_pin_mode("input_pullup", PIN_MAPPINGS[pin_id])
    return test_passed


'''
Checks all other pins to see if they are pulled high

/return True if all is OK otherwise False
'''
def check_remaining_pins(pin_id):
    for pin in PIN_MAPPINGS:
        if (pin != pin_id and pin != PIN_MAPPINGS[pin_id]):    #exclude pins under test
            if (read_pin(pin)[0] == "l"):
                print "Error while testing pin: "+str(pin_id)+" other pin("+str(pin)+") unexpectedly read low"
                return False
    return(True)


'''
Tests an entire Ruggeduino
'''
def run_test(port='/dev/ttyACM0'):
    test_passed = True
    global ser

    ser = serial.Serial(port, 115200, timeout=1, xonxoff=0, rtscts=0)

    # Wait for the Ruggeduino to boot
    time.sleep(2)

    ser.write("v")                #check version
    ser.flush()
    version = ser.readline()
    if (version[0:8] == "SRduino:1"):    #check version
        print "Unexpected Ruggeduino version received: "+version    #error on incorrect version
        return False

    for pin in PIN_MAPPINGS:
        set_pin_mode("input_pullup", pin)    #set pin to input pullup

    for pin in PIN_MAPPINGS:
        if not test_pin(pin):
            test_passed = False    #fail the test

    raw_input("\aSwitch to analogue test shield and press enter to continue.")

    for pin in ANALOGUE_PIN_MAPPINGS:        #for each analogue pin
        value = analogue_read_pin(ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin]])
        if value < 670 or value > 680:
            print "Error analogue pin ("+str(ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin]])+") did not read 3.3v value read:"+str(analogue_read_pin(ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin]]))
            test_passed = False    #test has failed

    ser.close()
    return test_passed


if __name__ == "__main__":
    if run_test():
        print "All tests completed successfully"
    else:
        print "broken board"
