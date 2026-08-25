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
    temp_file = STATE_FILE + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(state, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_file, STATE_FILE)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Choose Wisely</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* ==========================================================
         * SAGE & SUNSET ORANGE THEME
         * ========================================================== */
        :root {
            --bg-color: #f4f6f4;          /* Soft, muted sage-tinted background */
            --card-bg: #ffffff;           /* Clean white card */
            --text-main: #2c3531;         /* Deep, soft charcoal text (not harsh black) */
            --text-muted: #65746b;        /* Muted sage-grey for instructions */
            
            --accent-color: #e07a5f;      /* Sunset orange for primary actions */
            --accent-hover: #cc6b50;      /* Slightly deeper sunset orange */
            --accent-active: #81b29a;     /* Sage green highlight for the opened message */
            
            --locked-bg: #e2e8e4;         /* Soft neutral green-gray for locked buttons */
            --locked-text: #94a39b;       /* Muted text for disabled buttons */
            
            --border-radius: 16px;        /* Softly rounded corners */
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            text-align: center;
            padding: 20px;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
        }

        .card {
            background-color: var(--card-bg);
            padding: 40px 30px;
            border-radius: var(--border-radius);
            max-width: 420px;
            width: 100%;
            box-shadow: 0 10px 30px rgba(44, 53, 49, 0.06);
            border: 1px solid rgba(129, 178, 154, 0.2);
        }

        h2 {
            margin-top: 0;
            font-size: 1.6rem;
            letter-spacing: -0.02em;
            color: var(--text-main);
        }

        p {
            color: var(--text-muted);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .button-group {
            margin-top: 25px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        button {
            display: block;
            width: 100%;
            padding: 14px;
            font-size: 1rem;
            font-weight: 600;
            border: none;
            border-radius: calc(var(--border-radius) - 6px);
            cursor: pointer;
            background-color: var(--accent-color);
            color: #ffffff;
            transition: background-color 0.2s, transform 0.1s;
        }

        button:hover:not(:disabled) {
            background-color: var(--accent-hover);
        }

        button:active:not(:disabled) {
            transform: scale(0.98);
        }

        button:disabled {
            background-color: var(--locked-bg);
            color: var(--locked-text);
            cursor: not-allowed;
        }

        #result {
            margin-top: 25px;
            padding: 20px;
            background-color: #f7f9f7;
            border-left: 4px solid var(--accent-active);
            border-radius: 8px;
            text-align: left;
            word-break: break-word;
            border: 1px solid rgba(129, 178, 154, 0.15);
            border-left-width: 4px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>Choose One Message</h2>
        <p id="status">Once you select a message, the server will permanently lock the other two for everyone.</p>
        
        <div class="button-group">
            <button id="btn1" onclick="choose('1')">Message 1</button>
            <button id="btn2" onclick="choose('2')">Message 2</button>
            <button id="btn3" onclick="choose('3')">Message 3</button>
        </div>

        <div id="result" style="display:none;"></div>
    </div>

    <script>
        async function checkState() {
            try {
                let res = await fetch('/status?' + new Date().getTime());
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
                    b.style.backgroundColor = "var(--accent-active)";
                    b.innerText = `Message ${chosen} (Opened)`;
                } else {
                    b.innerText = `Message ${index + 1} (Locked)`;
                }
            });

            document.getElementById('status').innerText = "Choice permanently registered on server. Other options are locked.";
            let resBox = document.getElementById('result');
            resBox.style.display = "block";
            resBox.innerHTML = "<strong style='color: var(--accent-color);'>Message " + chosen + ":</strong><br><p style='margin-top:8px; color: var(--text-main);'>" + msg + "</p>";
        }

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

@app.route('/reset')
def reset_state():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    return "State has been reset!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
