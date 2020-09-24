from flask import Flask, request, Response
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

from threading import Thread

from controller import StateMachine, States

state_machine = StateMachine(initial_state=States.cava)
state_machine.start_loop()

app = Flask(__name__, static_folder='./react-web-app/build', static_url_path='/')
CORS(app)
PrometheusMetrics(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/controller')
def get_status():
    return {
        'currentState': str(state_machine.current_state),
        'loopThreadAlive': state_machine.loop_thread.is_alive(),
        'stateThreadAlive': state_machine.state_function_thread.is_alive()
    }

@app.route('/controller/mode/<mode>', methods=['PUT'])
def change_mode(mode: str):
    if not mode:
        return Response("Missing mode in uri path (/controller/mode/<mode>)")
    if mode in States._names():
        state_machine.command_queue.put(States.__dict__[mode])
        return Response(status=202)
    return Response(status=400)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
