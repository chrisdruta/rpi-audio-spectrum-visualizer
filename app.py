from flask import Flask
app = Flask(__name__, static_folder="./react-web-app/build", static_url_path="/")

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route('/status')
def get_status():
    return 'Hello, World!'

@app.route('/change-mode')
def put_mode():
    return 'Hello, World!'

if __name__ == "__main__":
    app.run(host="0.0.0.0")
