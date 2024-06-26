#!/usr/bin/python3

from flask import Flask, render_template, jsonify, request
from api.blueprint import app_views
from model import storage
from flask_cors import CORS
import logging
# from helper.loadenv import handleEnv

time_fmt = "%b %d %Y, %I:%M:%S %p"

# load_dotenv()
app = Flask(__name__, template_folder='static')
cors = CORS(app, resources={r"/*": {"origins": "*"}})


app.register_blueprint(app_views)

log_file = "error.json"
logger = logging.getLogger("error_logger")
log_level = logging.DEBUG
logger.setLevel(log_level)

log_handler = logging.FileHandler(log_file)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', time_fmt)
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"Error": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({"Error": "Forbidden"}), 403

@app.after_request
def log_errors(response):
    """This logs all server errors to the error.json file
    """

    if response.status_code > 401:
        error_message = {
            "status_code": response.status_code,
            "method": request.method,
            "path": request.path,
            "user_agent": request.user_agent.string,
            "remote_addr": request.remote_addr,
        }
        logger.error(error_message)
    return response

@app.teardown_appcontext
def close(exception):
    storage.reload()

@app.route("/")
def entry():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True, debug=True)
