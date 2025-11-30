import socketio
import sys

sio = socketio.Client(reconnection=True, reconnection_attempts=3)

@sio.on("connect")
def on_connect():
    print(" Connected successfully!")
    sio.disconnect()
    sys.exit(0)

@sio.on("connect_error")
def on_error(data):
    print(f" Connection error: {data}")

try:
    print(" Testing connection to https://tgctest.onrender.com...")
    sio.connect("https://tgctest.onrender.com", transports=["websocket", "polling"], wait_timeout=30)
    sio.wait()
except Exception as e:
    print(f" Exception: {e}")
    sys.exit(1)
