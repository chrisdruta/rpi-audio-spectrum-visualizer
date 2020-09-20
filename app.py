from flask import Flask, request, Response
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

from threading import Lock, Thread
from controller import StateMachine, States

buffer = [States.idle]
buffer_lock = Lock()
state_machine = StateMachine(buffer, buffer_lock)

# thread handler
thread = Thread(target=state_machine.start_loop)
thread.start()

app = Flask(__name__, static_folder="./react-web-app/build", static_url_path="/")
CORS(app)
PrometheusMetrics(app)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/controller")
def get_status():
    with buffer_lock:
        return {
            "stateBuffer": str(buffer),
            "threadAlive": thread.is_alive()
        }

@app.route("/controller/mode", methods=["POST"])
def change_mode():
    req_body = request.json
    if "state" in req_body and req_body["state"] in States._names():
        state_machine.set_state(req_body["state"])
        return Response(status=202)
    return Response(status=400)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
