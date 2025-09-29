from flask import Flask, request, jsonify, g
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import time
import os
import traceback

app = Flask(__name__)
app.json.sort_keys = False  # keep JSON response order


# ---- JSON Formatter (writes raw JSON dicts) ----
class JsonFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, dict):
            return json.dumps(record.msg)
        return json.dumps({"message": str(record.msg)})


# ---- Setup loggers with rotation ----
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)

# Access Logger (rotates daily, keep 7 days)
access_handler = TimedRotatingFileHandler(
    os.path.join(log_dir, "access.log"), when="D", interval=1, backupCount=7, encoding="utf-8"
)
access_handler.setFormatter(JsonFormatter())
access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)
access_logger.addHandler(access_handler)

# Application Logger (rotates daily, keep 7 days)
app_handler = TimedRotatingFileHandler(
    os.path.join(log_dir, "application.log"), when="D", interval=1, backupCount=7, encoding="utf-8"
)
app_handler.setFormatter(JsonFormatter())
application_logger = logging.getLogger("application_logger")
application_logger.setLevel(logging.INFO)
application_logger.addHandler(app_handler)


# ---- Track request start time ----
@app.before_request
def start_timer():
    g.start_time = time.time()


# ---- Log access after response ----
@app.after_request
def log_response(response):
    duration = round(time.time() - g.start_time, 4)
    log_entry = {
        "event": "access_log",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "method": request.method,
        "path": request.path,
        "status_code": response.status_code,
        "remote_addr": request.headers.get('X-Forwarded-For', request.remote_addr),
        "user_agent": request.headers.get("User-Agent"),
        "duration_seconds": duration
    }
    access_logger.info(log_entry)
    return response


# ---- API Route ----
@app.route('/time-series', methods=['GET'])
def index():
    now = datetime.now().isoformat()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Inner trace steps
    trace_steps = [
        "Step 1: Received request at index endpoint",
        "Step 2: Retrieved client IP",
        "Step 3: Generated timestamp",
        "Step 4: Prepared response JSON"
    ]

    log_entry = {
        "event": "application_log",
        "trace": trace_steps,
        "message": "Index endpoint executed successfully",
        "timestamp": now,
        "ip": ip
    }
    application_logger.info(log_entry)

    return jsonify({
        "timestamp": now,
        "ip": ip
    })


# ---- Error Handlers ----
@app.errorhandler(404)
def not_found(e):
    log_entry = {
        "event": "application_log",
        "trace": ["Error handler triggered", "Returned 404 Not Found"],
        "message": f"Resource not found: {request.path}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr)
    }
    application_logger.warning(log_entry)
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(500)
def internal_error(e):
    log_entry = {
        "event": "application_log",
        "trace": ["Error handler triggered", "Returned 500 Internal Server Error"],
        "message": f"Internal server error at {request.path}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr)
    }
    application_logger.error(log_entry)
    return jsonify({"error": "Internal Server Error"}), 500


# ---- Catch-all Exception Handler ----
@app.errorhandler(Exception)
def handle_exception(e):
    log_entry = {
        "event": "application_log",
        "trace": ["Unhandled exception occurred"],
        "message": str(e),
        "stacktrace": traceback.format_exc(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr)
    }
    application_logger.error(log_entry)
    return jsonify({"error": "Unexpected Server Error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
