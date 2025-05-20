from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)
DATA_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f)

def calculate_lazy_score(tasks):
    """
    귀찮음 점수 = 미룬 횟수(postponed) 기준
    3회 이상이면 귀찮음 상태로 판단
    """
    total_postpones = sum(task.get("postponed", 0) for task in tasks)
    return total_postpones

@app.route("/")
def index():
    tasks = load_tasks()
    lazy_score = calculate_lazy_score(tasks)
    is_lazy = lazy_score >= 3
    return render_template("index.html", tasks=tasks, lazy=is_lazy, lazy_score=lazy_score)

@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    time = request.form["time"]
    tasks = load_tasks()
    tasks.append({"title": title, "time": time, "done": False, "postponed": 0})
    save_tasks(tasks)
    return redirect("/")

@app.route("/done/<int:index>")
def done(index):
    tasks = load_tasks()
    tasks[index]["done"] = True
    save_tasks(tasks)
    return redirect("/")

@app.route("/postpone/<int:index>")
def postpone(index):
    tasks = load_tasks()
    tasks[index]["postponed"] = tasks[index].get("postponed", 0) + 1
    save_tasks(tasks)
    return redirect("/")

@app.route("/reset")
def reset():
    save_tasks([])
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
