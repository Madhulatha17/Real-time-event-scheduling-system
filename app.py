from flask import Flask, request, redirect, render_template_string, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "eventflow"

events = []
next_id = 1


# ---------- AVL TREE ----------
class Node:
    def __init__(self, event):
        self.event = event
        self.left = None
        self.right = None
        self.height = 1


def height(node):
    return node.height if node else 0


def balance(node):
    return height(node.left) - height(node.right) if node else 0


def key(event):
    return (event["date"], event["start"], event["id"])


def right_rotate(y):
    x = y.left
    temp = x.right
    x.right = y
    y.left = temp
    y.height = 1 + max(height(y.left), height(y.right))
    x.height = 1 + max(height(x.left), height(x.right))
    return x


def left_rotate(x):
    y = x.right
    temp = y.left
    y.left = x
    x.right = temp
    x.height = 1 + max(height(x.left), height(x.right))
    y.height = 1 + max(height(y.left), height(y.right))
    return y


def insert(root, event):
    if root is None:
        return Node(event)

    if key(event) < key(root.event):
        root.left = insert(root.left, event)
    else:
        root.right = insert(root.right, event)

    root.height = 1 + max(height(root.left), height(root.right))
    bf = balance(root)

    if bf > 1 and key(event) < key(root.left.event):
        return right_rotate(root)

    if bf < -1 and key(event) > key(root.right.event):
        return left_rotate(root)

    if bf > 1 and key(event) > key(root.left.event):
        root.left = left_rotate(root.left)
        return right_rotate(root)

    if bf < -1 and key(event) < key(root.right.event):
        root.right = right_rotate(root.right)
        return left_rotate(root)

    return root


def build_tree():
    root = None
    for event in events:
        root = insert(root, event)
    return root


def inorder(root, result=None):
    if result is None:
        result = []
    if root:
        inorder(root.left, result)
        result.append(root.event)
        inorder(root.right, result)
    return result


# ---------- CONFLICT DETECTION ----------
def find_conflict(day, start, end, ignore_id=None):
    for event in events:
        if event["id"] == ignore_id:
            continue
        if event["date"] == day and start < event["end"] and end > event["start"]:
            return event
    return None


def valid_times(day, start, end):
    try:
        datetime.strptime(day, "%Y-%m-%d")
        datetime.strptime(start, "%H:%M")
        datetime.strptime(end, "%H:%M")
        return start < end
    except ValueError:
        return False


# ---------- WEBSITE ----------
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>EventFlow Scheduler</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f1f3ff;
            color: #202444;
        }
        header {
            background: #171936;
            color: white;
            padding: 25px;
            text-align: center;
        }
        nav {
            background: white;
            padding: 15px;
            text-align: center;
        }
        nav a {
            margin: 12px;
            color: #604cff;
            text-decoration: none;
            font-weight: bold;
        }
        main {
            max-width: 1000px;
            margin: 25px auto;
            padding: 15px;
        }
        .panel {
            background: white;
            padding: 22px;
            margin-bottom: 20px;
            border-radius: 14px;
            box-shadow: 0 3px 12px #0000000c;
        }
        input {
            box-sizing: border-box;
            padding: 11px;
            margin: 6px 0 15px;
            width: 100%;
            border: 1px solid #ddd;
            border-radius: 7px;
        }
        button {
            background: #6855f5;
            color: white;
            padding: 11px 16px;
            border: none;
            border-radius: 7px;
            cursor: pointer;
        }
        .delete { background: #e74c61; }
        .event {
            background: #f8f7ff;
            border: 1px solid #e3dfff;
            border-radius: 10px;
            padding: 15px;
            margin: 12px 0;
        }
        .message {
            padding: 12px;
            background: #fff1f0;
            border-radius: 8px;
        }
    </style>
</head>
<body>
<header>
    <h1>✦ EventFlow</h1>
    <p>Real-Time Event Scheduling System</p>
    <small>DSA Micro Project | CO3 · CO4 · CO5</small>
</header>

<nav>
    <a href="/">Dashboard</a>
    <a href="/#create">Create Event</a>
    <a href="/tree">AVL Tree</a>
    <a href="/compare">AVL vs BST</a>
</nav>

<main>
    {% with messages = get_flashed_messages() %}
        {% for message in messages %}
            <div class="panel message">{{ message }}</div>
        {% endfor %}
    {% endwith %}

    <div class="panel">
        <h2>📊 Dashboard</h2>
        <h3>Total Events: {{ events|length }}</h3>
        <p>AVL Tree Height: {{ tree_height }}</p>
        <p>Events are displayed in chronological order.</p>
    </div>

    <div class="panel" id="create">
        <h2>＋ Create an Event</h2>
        <form method="post" action="/add">
            <label>Event Name</label>
            <input name="name" placeholder="e.g. DSA Workshop" required>

            <label>Date</label>
            <input type="date" name="date" required>

            <label>Start Time</label>
            <input type="time" name="start" required>

            <label>End Time</label>
            <input type="time" name="end" required>

            <label>Venue</label>
            <input name="venue" placeholder="e.g. Seminar Hall" required>

            <button type="submit">Add Event</button>
        </form>
    </div>

    <div class="panel">
        <h2>📅 Scheduled Events</h2>
        <form method="get" action="/">
            <input name="q" placeholder="Search event name or ID" value="{{ q }}">
            <button type="submit">Search</button>
        </form>

        {% for e in events %}
            <div class="event">
                <h3>{{ e.name }} — Event #{{ e.id }}</h3>
                <p>📅 {{ e.date }}</p>
                <p>⏰ {{ e.start }} to {{ e.end }}</p>
                <p>📍 {{ e.venue }}</p>

                <form method="post" action="/delete/{{ e.id }}"
                      onsubmit="return confirm('Delete this event?')"
                      style="display:inline">
                    <button class="delete">Delete</button>
                </form>
                <a href="/edit/{{ e.id }}">Reschedule</a>
            </div>
        {% else %}
            <p>No events found.</p>
        {% endfor %}
    </div>
</main>
</body>
</html>
"""


@app.route("/")
def home():
    root = build_tree()
    ordered = inorder(root)
    q = request.args.get("q", "").strip().lower()

    if q:
        ordered = [
            e for e in ordered
            if q in e["name"].lower() or q == str(e["id"])
        ]

    return render_template_string(
        HTML,
        events=ordered,
        q=q,
        tree_height=height(root)
    )


@app.route("/add", methods=["POST"])
def add():
    global next_id

    name = request.form.get("name", "").strip()
    day = request.form.get("date", "")
    start = request.form.get("start", "")
    end = request.form.get("end", "")
    venue = request.form.get("venue", "").strip()

    if not name or not venue or not valid_times(day, start, end):
        flash("Invalid details. Check the date and time.")
        return redirect("/#create")

    conflict = find_conflict(day, start, end)

    if conflict:
        flash(
            f"Time conflict with {conflict['name']} "
            f"({conflict['start']}–{conflict['end']})."
        )
        return redirect("/#create")

    events.append({
        "id": next_id,
        "name": name,
        "date": day,
        "start": start,
        "end": end,
        "venue": venue
    })

    next_id += 1
    flash("Event added successfully!")
    return redirect("/")


@app.route("/delete/<int:event_id>", methods=["POST"])
def delete(event_id):
    global events
    events = [e for e in events if e["id"] != event_id]
    flash("Event deleted successfully!")
    return redirect("/")


@app.route("/edit/<int:event_id>", methods=["GET", "POST"])
def edit(event_id):
    event = next((e for e in events if e["id"] == event_id), None)

    if event is None:
        flash("Event not found.")
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        day = request.form.get("date", "")
        start = request.form.get("start", "")
        end = request.form.get("end", "")
        venue = request.form.get("venue", "").strip()

        if not name or not venue or not valid_times(day, start, end):
            flash("Invalid event details.")
            return redirect(f"/edit/{event_id}")

        conflict = find_conflict(day, start, end, event_id)

        if conflict:
            flash(f"Conflict with {conflict['name']}.")
            return redirect(f"/edit/{event_id}")

        event.update({
            "name": name,
            "date": day,
            "start": start,
            "end": end,
            "venue": venue
        })

        flash("Event rescheduled successfully!")
        return redirect("/")

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reschedule Event</title>
        <style>
            body { font-family: Arial; background: #f1f3ff; padding: 30px; }
            form { background: white; padding: 25px; border-radius: 12px; max-width: 500px; }
            input { box-sizing: border-box; width: 100%; padding: 10px; margin: 8px 0 15px; }
            button { padding: 10px 16px; background: #6855f5; color: white; border: 0; }
        </style>
    </head>
    <body>
        <h1>Reschedule Event</h1>
        {% with messages = get_flashed_messages() %}
          {% for message in messages %}
            <script>alert({{ message|tojson }});</script>
          {% endfor %}
        {% endwith %}
        <form method="post">
            Name: <input name="name" value="{{ e.name }}" required>
            Date: <input type="date" name="date" value="{{ e.date }}" required>
            Start: <input type="time" name="start" value="{{ e.start }}" required>
            End: <input type="time" name="end" value="{{ e.end }}" required>
            Venue: <input name="venue" value="{{ e.venue }}" required>
            <button type="submit">Save Changes</button>
        </form>
        <p><a href="/">Back to Dashboard</a></p>
    </body>
    </html>
    """, e=event)


@app.route("/tree")
def tree_page():
    root = build_tree()
    ordered = inorder(root)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>AVL Tree</title></head>
    <body style="font-family:Arial;background:#f1f3ff;padding:25px">
        <h1>🌳 AVL Tree Information</h1>
        <div style="background:white;padding:20px;border-radius:12px">
            <h3>Total Nodes: {{ count }}</h3>
            <h3>Tree Height: {{ tree_height }}</h3>
            <h3>In-order Traversal</h3>
            <p>{{ names }}</p>
            <table border="1" cellpadding="10">
                <tr><th>ID</th><th>Event</th><th>Date</th><th>Time</th></tr>
                {% for e in events %}
                <tr>
                    <td>{{ e.id }}</td>
                    <td>{{ e.name }}</td>
                    <td>{{ e.date }}</td>
                    <td>{{ e.start }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <p><a href="/">Back to Dashboard</a></p>
    </body>
    </html>
    """, count=len(ordered), tree_height=height(root),
       names=" → ".join(e["name"] for e in ordered), events=ordered)


@app.route("/compare")
def compare():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>AVL vs BST</title></head>
    <body style="font-family:Arial;background:#f1f3ff;padding:25px">
        <h1>AVL Tree vs Normal BST</h1>
        <table border="1" cellpadding="12" style="background:white">
            <tr><th>Operation</th><th>AVL Tree</th><th>Normal BST Worst Case</th></tr>
            <tr><td>Search</td><td>O(log n)</td><td>O(n)</td></tr>
            <tr><td>Insertion</td><td>O(log n)</td><td>O(n)</td></tr>
            <tr><td>Deletion</td><td>O(log n)</td><td>O(n)</td></tr>
        </table>
        <p>AVL trees use rotations to maintain balance.</p>
        <p><a href="/">Back to Dashboard</a></p>
    </body>
    </html>
    """)


if __name__ == "__main__":
    print("EventFlow is running at http://127.0.0.1:5000")
    app.run(debug=True)
