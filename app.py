from flask import Flask, render_template_string, jsonify, request
import json
import os

app = Flask(__name__)

# File to act as persistent state on the server
STATE_FILE = "state.json"

# YOUR THREE MESSAGES
MESSAGES = {
    "1": "This is Secret Message #1.",
    "2": "This is Secret Message #2.",
    "3": "This is Secret Message #3."
}

def get_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"chosen_option": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>One-Time Choice</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #fff; text-align: center; padding: 50px; }
        .card { background: #1e293b; padding: 30px; border-radius: 12px; max-width: 400px; margin: auto; }
        button { display: block; width: 100%; margin: 10px 0; padding: 12px; font-size: 16px; border: none; border-radius: 6px; cursor: pointer; background: #0284c7; color: white; }
        button:disabled { background: #334155; color: #64748b; cursor: not-allowed; }
        #result { margin-top: 20px; padding: 15px; background: #0f172a; border-left: 4px solid #38bdf8; text-align: left; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Choose One Message</h2>
        <p id="status">Once you select a message, the server will permanently lock the other two.</p>
        <button id="btn1" onclick="choose('1')">Message 1</button>
        <button id="btn2" onclick="choose('2')">Message 2</button>
        <button id="btn3" onclick="choose('3')">Message 3</button>

        <div id="result" style="display:none;"></div>
    </div>

    <script>
        async function checkState() {
            let res = await fetch('/status');
            let data = await res.json();
            if (data.chosen_option) {
                applyLock(data.chosen_option, data.message);
            }
        }

        async function choose(option) {
            let res = await fetch('/choose', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ choice: option })
            });
            let data = await res.json();
            if (data.success) {
                applyLock(option, data.message);
            } else {
                alert(data.error);
                checkState();
            }
        }

        function applyLock(chosen, msg) {
            document.querySelectorAll('button').forEach(b => b.disabled = true);
            document.getElementById('status').innerText = "Choice permanently registered on server.";
            let resBox = document.getElementById('result');
            resBox.style.display = "block";
            resBox.innerHTML = "<strong>Message " + chosen + ":</strong><br>" + msg;
        }

        checkState();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/status', methods=['GET'])
def status():
    state = get_state()
    chosen = state.get("chosen_option")
    if chosen:
        return jsonify({"chosen_option": chosen, "message": MESSAGES[chosen]})
    return jsonify({"chosen_option": None})

@app.route('/choose', methods=['POST'])
def choose():
    state = get_state()
    if state.get("chosen_option") is not None:
        return jsonify({"success": False, "error": "A choice has already been made and locked!"}), 400
    
    req_data = request.get_json()
    choice = str(req_data.get("choice"))
    
    if choice in MESSAGES:
        state["chosen_option"] = choice
        save_state(state)
        return jsonify({"success": True, "message": MESSAGES[choice]})
    
    return jsonify({"success": False, "error": "Invalid choice"}), 400

if __name__ == '__main__':
    app.run(port=5000)