from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# In-memory store — fine for this project, you'll swap for a real DB later if you want
tasks = []
next_id = 1


@app.route("/health", methods=["GET"])
def health():
    """Used by monitoring / load balancer healthchecks later on."""
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()}), 200


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id
    data = request.get_json(silent=True)

    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    task = {
        "id": next_id,
        "title": data["title"],
        "done": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    tasks.append(task)
    next_id += 1

    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]

    if len(tasks) == before:
        return jsonify({"error": "task not found"}), 404

    return "", 204


if __name__ == "__main__":
    # Bind to localhost only — nginx will be the one exposed to the internet
    app.run(host="127.0.0.1", port=5000)
