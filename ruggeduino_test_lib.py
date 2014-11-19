#!/bin/python
import serial
import time
ser = None


PIN_MODE_FLAGS = {
    'high': 'h',
    'low': 'l',

    'input': 'i',
    'output': 'o',
    'input_pullup': 'p',
}


def set_pin_mode(mode, pin_id):
    """Sets a pin's value or mode, according to the `mode` parameter."""
    pin_mode_char = PIN_MODE_FLAGS[mode]
    pin_id_char = chr(ord('a')+pin_id)

    ser.write(pin_mode_char + pin_id_char)
    ser.flush()
    ser.readline()   # clear any return from the Ruggeduino


def read_pin(pin_id):
    """Returns the value on a pin."""
    ser.write("r"+chr(ord('a')+pin_id))
    ser.flush()
    return ser.readline()


def analogue_read_pin(pin_id):
    """Reads the analogue value on a pin."""
    ser.write("a"+chr(ord('a')+pin_id))
    ser.flush()
    return int(ser.readline())


# Mapping of pins to their partners on the test harness
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

ANALOGUE_ERROR_MESSAGE = "Error: analogue pin {pin_id} did not read {expected}. Value read: {actual}"

def test_pin(pin_id):
    """
    Performs a test sequence on a pin

    /param pin_id pin id to test
    /return True if all is OK otherwise False
    """

    test_passed = True
    partner_pin_id = PIN_MAPPINGS[pin_id]

    # Set up pins
    set_pin_mode("output", pin_id)
    set_pin_mode("high", pin_id)
    set_pin_mode("input", partner_pin_id)

    if read_pin(partner_pin_id)[0] != "h":
        print "Error while testing pin", pin_id, ": Pin pair read low when expecting high (stuck at low error)"
        test_passed = False

    if not check_remaining_pins(pin_id):
        test_passed = False

    if partner_pin_id in ANALOGUE_PIN_MAPPINGS:
        analogue_partner_id = ANALOGUE_PIN_MAPPINGS[partner_pin_id]
        analogue_value = analogue_read_pin(analogue_partner_id)
        if analogue_value < 940:
            print ANALOGUE_ERROR_MESSAGE.format(pin_id=analogue_partner_id,
                    expected="max", actual=analogue_value)

    set_pin_mode("low", pin_id)

    if read_pin(partner_pin_id)[0] != "l":
        print "Error while testing pin", pin_id, ": Pin pair read high when expecting low (stuck at high error)"
        test_passed = False

    if not check_remaining_pins(pin_id):
        test_passed = False

    if partner_pin_id in ANALOGUE_PIN_MAPPINGS:
        analogue_partner_id = ANALOGUE_PIN_MAPPINGS[partner_pin_id]
        analogue_value = analogue_read_pin(analogue_partner_id)
        if analogue_value > 10:
            print ANALOGUE_ERROR_MESSAGE.format(pin_id=analogue_partner_id,
                    expected="min", actual=analogue_value)

    # Return test pins to normal
    set_pin_mode("input_pullup", pin_id)
    set_pin_mode("input_pullup", partner_pin_id)
    return test_passed


def check_remaining_pins(pin_id):
    """
    Checks all pins except the one with the given ID to see if they are pulled
    high.

    /return True if all is OK otherwise False
    """
    for pin in PIN_MAPPINGS:
        if pin != pin_id and pin != PIN_MAPPINGS[pin_id]:
            if read_pin(pin)[0] == "l":
                print "Error: while testing pin", pin_id, "another pin", pin, "unexpectedly read low"
                return False

    return True


def run_test(port='/dev/ttyACM0'):
    """Tests an entire Ruggeduino."""
    test_passed = True
    global ser

    ser = serial.Serial(port, 115200, timeout=1, xonxoff=0, rtscts=0)

    # Wait for the Ruggeduino to boot
    time.sleep(2)

    # Check version
    ser.write("v")
    ser.flush()
    version = ser.readline()
    if (version[0:8] == "SRduino:1"):
        print "Unexpected Ruggeduino version received:", version
        return False

    for pin in PIN_MAPPINGS:
        set_pin_mode("input_pullup", pin)

    for pin in PIN_MAPPINGS:
        if not test_pin(pin):
            test_passed = False

    raw_input("\aSwitch to analogue test shield and press enter to continue.")

    for pin in ANALOGUE_PIN_MAPPINGS:
        analogue_pin_id = ANALOGUE_PIN_MAPPINGS[PIN_MAPPINGS[pin]]
        value = analogue_read_pin(analogue_pin_id)
        if value < 670 or value > 680:
            print ANALOGUE_ERROR_MESSAGE.format(pin_id=analogue_pin_id,
                    expected="3.3v", actual=value)
            test_passed = False

    ser.close()
    return test_passed


if __name__ == "__main__":
    if run_test():
        print "All tests completed successfully"
    else:
        print "broken board"
