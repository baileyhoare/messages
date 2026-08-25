from flask import Flask, render_template_string, jsonify, request
import json
import os

app = Flask(__name__)

STATE_FILE = "state.json"

# YOUR THREE MESSAGES
MESSAGES = {
    "1": "This is Secret Message #1.",
    "2": "This is Secret Message #2.",
    "3": "This is Secret Message #3."
}

def get_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"chosen_option": None}

def save_state(state):
    # Write to a temp file first, then replace to prevent race conditions/corruption
    temp_file = STATE_FILE + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(state, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_file, STATE_FILE)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>One-Time Choice</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #fff; text-align: center; padding: 30px; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .card { background: #1e293b; padding: 30px; border-radius: 12px; max-width: 400px; width: 100%; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
        button { display: block; width: 100%; margin: 10px 0; padding: 12px; font-size: 16px; border: none; border-radius: 6px; cursor: pointer; background: #0284c7; color: white; font-weight: bold; transition: background 0.2s; }
        button:hover:not(:disabled) { background: #0369a1; }
        button:disabled { background: #334155; color: #64748b; cursor: not-allowed; }
        #result { margin-top: 20px; padding: 15px; background: #0f172a; border-left: 4px solid #38bdf8; text-align: left; word-break: break-word; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Choose One Message</h2>
        <p id="status">Once you select a message, the server will permanently lock the other two for everyone.</p>
        <button id="btn1" onclick="choose('1')">Message 1</button>
        <button id="btn2" onclick="choose('2')">Message 2</button>
        <button id="btn3" onclick="choose('3')">Message 3</button>

        <div id="result" style="display:none;"></div>
    </div>

    <script>
        async function checkState() {
            try {
                let res = await fetch('/status?' + new Date().getTime()); // prevent caching
                let data = await res.json();
                if (data.chosen_option) {
                    applyLock(data.chosen_option, data.message);
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function choose(option) {
            if (!confirm("Are you sure? Once chosen, the other two messages will lock forever.")) return;
            
            try {
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
            } catch (e) {
                alert("Network error. Please try again.");
                checkState();
            }
        }

        function applyLock(chosen, msg) {
            document.querySelectorAll('button').forEach((b, index) => {
                b.disabled = true;
                if ((index + 1).toString() === chosen) {
                    b.style.backgroundColor = "#0369a1";
                    b.innerText = `Message ${chosen} (Opened)`;
                } else {
                    b.innerText = `Message ${index + 1} (Locked)`;
                }
            });

            document.getElementById('status').innerText = "Choice permanently registered on server. Other options are locked.";
            let resBox = document.getElementById('result');
            resBox.style.display = "block";
            resBox.innerHTML = "<strong style='color: #38bdf8;'>Message " + chosen + ":</strong><br><p style='margin-top:5px;'>" + msg + "</p>";
        }

        // Check state on load and poll every 3 seconds just in case
        checkState();
        setInterval(checkState, 3000);
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
        return jsonify({"success": False, "error": "A choice has already been made and locked by someone else!"}), 400
    
    req_data = request.get_json()
    choice = str(req_data.get("choice"))
    
    if choice in MESSAGES:
        state["chosen_option"] = choice
        save_state(state)
        return jsonify({"success": True, "message": MESSAGES[choice]})
    
    return jsonify({"success": False, "error": "Invalid choice"}), 400

# Optional test reset route (remove before sending final link if you want)
@app.route('/reset')
def reset_state():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    return "State has been reset!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
