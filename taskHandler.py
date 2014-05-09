from bottle import route, run, template, static_file, Bottle, abort, request
from time import sleep, localtime, strftime, time
import json
import atexit
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
import multiprocessing

DEBUG = False
if not DEBUG:
  from openwest import OpenWestHardware

class CustomWebSocket(multiprocessing.Process):

  def __init__(self, taskQ):
    multiprocessing.Process.__init__(self)
    self.taskQ = taskQ

    if not DEBUG:
      self.hw = OpenWestHardware()
      self.switch_state = self.hw.is_switch_on()
      self.last_sensor_update = time()
      atexit.register(self.hw.cleanup)

    self.app = Bottle()

    @self.app.route('/ws')
    def handle_websocket():
      wsock = request.environ.get('wsgi.websocket')
      if not wsock:
          abort(400, 'Expected WebSocket request.')

      print "Socket connected"

      while True:
          try:
            # wsock.send("I'm still connected")

            # Push state information to the browser for some of the peripherals
            if not DEBUG:

              # ========= BUTTON PRESSES =========
              if self.hw.is_button_pressed():
                wsock.send(json.dumps({"button": True}))
                sleep(.8)

              # ========= SWITCH STATE =========
              if self.switch_state != self.hw.is_switch_on():
                self.switch_state = self.hw.is_switch_on();
                wsock.send(json.dumps({"switch": self.switch_state}))

              # ========= RFID =========
              rfid = self.hw.check_for_rfid_scan()
              if(rfid != None and len(rfid) > 0):
                wsock.send(json.dumps({"rfid": rfid}))

              # ========= SENSORS =========
              if((time() - self.last_sensor_update) >= 5):
                self.last_sensor_update = time()
                temp = self.hw.get_temp()
                wsock.send(json.dumps({"temp": temp}))



            # Are any tasks queued
            if not self.taskQ.empty():
              task = self.taskQ.get()

              print "SocketHandler received: " + str(task)
              
              if "device" in task:
                # ========= LED =========
                if(task["device"] == "led"):
                  print "Changing led state to :" + str(task["state"])
                  
                  if not DEBUG:
                    self.hw.set_led(task["state"])
                  else:
                    wsock.send(json.dumps({"led": True}))

                # ========= RELAY =========
                elif(task["device"] == "relay"):
                  if not DEBUG:
                    self.hw.set_relay_state(int(task["id"]), task["state"])
                  else:
                    wsock.send("Setting Relay " + str(task["id"]) + " to " + str(task["state"]))

                # ========= DISPLAY =========
                elif(task["device"] == "display"):
                  if not DEBUG:
                    self.hw.set_display(str(task["text"]))
                  else:
                    wsock.send("Setting display text to " + str(task["text"]))

                else:
                  wsock.send("Unrecognized device" + task["device"]);
              else:
                print "Task didn't contain device key"


          except WebSocketError:
              break

      print "Socket closed"

  def close(self):
    print "Closing CustomWebSocket"

  def run(self):

    self.server = WSGIServer(("0.0.0.0", 8080), self.app,
                      handler_class=WebSocketHandler)
    self.server.serve_forever()
