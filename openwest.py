import RPi.GPIO as GPIO
import spidev
from time import sleep, localtime, strftime, time
import sys
import smbus
import serial

class OpenWestHardware(object):

  def __init__(self):

    GPIO.setmode(GPIO.BOARD)

    # Setup the LED pin as an output and to have an initial 
    # state of high which turns the LED off
    GPIO.setup(12, GPIO.OUT, initial=GPIO.HIGH)

    # Setup the switch pin as an input
    GPIO.setup(16, GPIO.IN)

    # Setup the button pin as an input
    GPIO.setup(18, GPIO.IN)

    # Setup spi module
    self.spi = spidev.SpiDev()
    self.spi.open(0,0)

    # Setup i2c module
    self.i2c = smbus.SMBus(1)

    # Setup serial port
    self.sp = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=0.1)

    # Setup relays
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)



  def get_temp(self):
    temp = self.i2c.read_word_data(0x48, 0)
    byte1_mask = 0b0000000011111111
    byte2_mask = 0b1111111100000000
    byte1 = (temp & byte1_mask) << 4
    byte2 = (temp & byte2_mask) >> 12
    temp_c = byte2 | byte1
    temp_c *= .0625
    temp_f = temp_c*1.80 + 32.00
    return round(temp_f,2)

  def spi_send(self, data):
    xfer_list = []
    if type(data) == str:
      for c in data:
        xfer_list.append(ord(c))
    elif type(data) == list:
      xfer_list += data
    elif type(data) == int:
      xfer_list.append(data)
    else:
      print "Unsupported type passed to spi_send. Must be str, int, or list"

    self.spi.xfer2(xfer_list, 250000)

  def clear_display(self):
    self.spi_send([0x76])

  def display_time(self):
    t = strftime("%H%M", localtime())
    self.clear_display()
    self.spi_send(t)
    self.spi_send([0x77, 0x10])

  def display_temp(self, temp):
    # Display temp with one decimal of precision
    temp_str = "{:4.1f}f".format(round(temp,1))
    display_val = temp_str.replace('.','')
    self.clear_display()
    self.spi_send(display_val)
    # Turn on the decimal and the apostrophe
    self.spi_send([0x77, 0x22])

  def set_display(self, display_val):
    self.clear_display()
    self.spi_send(display_val)

  def set_led(self, state):
    GPIO.output(12, not state);

  def is_button_pressed(self):
    return GPIO.input(18) == GPIO.HIGH

  def is_switch_on(self):
    return GPIO.input(16) == GPIO.HIGH

  def check_for_rfid_scan(self):
    rfid = self.sp.readline()
    #print rfid
    if (rfid == None or rfid == "" or rfid == chr(2)):
      return None
    elif (rfid[0] == chr(3) or rfid[0] == chr(2)):
      return rfid[1:].strip()

  def set_relay_state(self, relay_num, relay_state):
    if relay_num == 1:
      GPIO.output(11, relay_state)
    elif relay_num == 2:
      GPIO.output(13, relay_state)
    elif relay_num == 3:
      GPIO.output(15, relay_state)
    else:
      print "Unrecognized relay number"


  def cleanup(self):
    GPIO.output(12, GPIO.HIGH)
    GPIO.output(11, GPIO.LOW)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)
    GPIO.cleanup()
    self.clear_display()
    self.spi.close()
  