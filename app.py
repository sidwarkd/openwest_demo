from bottle import route, run, template, static_file, get, post, request, Bottle
from time import sleep
import atexit
import multiprocessing
import taskHandler

app = Bottle()

# Before we start the web server let's set up the Task queue
taskQ = multiprocessing.Queue()

socketProcess = taskHandler.CustomWebSocket(taskQ)
socketProcess.daemon = True
socketProcess.start()

@route('/')
def index():
  return static_file('index1.html', root='./views')

@post('/hw')
def hw_service():
  taskQ.put(request.json)
  return {"status": "ok"}

@route('<filepath:path>')
def serve_static(filepath):
  return static_file(filepath, root='./public')



run(host='0.0.0.0', port=8000)