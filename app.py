from flask import Flask, render_template_string, jsonify, request
import json
import os

app = Flask(__name__)

STATE_FILE = "state.json"

# ==========================================
# CONFIGURATION
# ==========================================
SECURITY_QUESTION = "What is this guy's name?"
# Replace with your direct image URL, or leave as "" for text-only
SECURITY_IMAGE_URL = "/static/lorentz.jpg"

ACCEPTED_ANSWERS = ["Lorentz", "lorentz"]

# Paste your Spotify Playlist embed link or ID here
# Example format: "https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0"
SPOTIFY_EMBED_URL = "https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0"

# INTRO MESSAGE - shown as a scrollable popup right after the security question is passed
INTRO_TITLE = "Before you choose..."
INTRO_MESSAGE = """
Write whatever you'd like the person to read here.

It can be as long as you want — this box scrolls, so
feel free to write a few paragraphs. They'll need to
click "I've read this" before they can pick a message.
"""

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
    return {"chosen_option": None, "authenticated": False}

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
    <title>Security Question</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg-color: #f4f6f4;
            --card-bg: #ffffff;
            --text-main: #2c3531;
            --text-muted: #65746b;
            --accent-color: #e07a5f;
            --accent-hover: #cc6b50;
            --accent-active: #81b29a;
            --locked-bg: #e2e8e4;
            --locked-text: #94a39b;
            --border-radius: 16px;
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
            padding: 35px 30px;
            border-radius: var(--border-radius);
            max-width: 440px;
            width: 100%;
            box-shadow: 0 10px 30px rgba(44, 53, 49, 0.06);
            border: 1px solid rgba(129, 178, 154, 0.2);
            box-sizing: border-box;
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

        .question-image {
            width: 100%;
            max-height: 200px;
            object-fit: cover;
            border-radius: calc(var(--border-radius) - 8px);
            margin-bottom: 15px;
            border: 1px solid rgba(129, 178, 154, 0.2);
        }

        .spotify-container {
            margin: 20px 0 15px 0;
            border-radius: 12px;
            overflow: hidden;
        }

        .input-group, .button-group {
            margin-top: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        input[type="text"] {
            width: 100%;
            padding: 12px 14px;
            font-size: 1rem;
            border: 1px solid #cbd5e1;
            border-radius: calc(var(--border-radius) - 6px);
            box-sizing: border-box;
            background-color: #f8fafc;
            color: var(--text-main);
            outline: none;
            transition: border-color 0.2s;
        }

        input[type="text"]:focus {
            border-color: var(--accent-color);
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

        .hidden { display: none !important; }

        /* ===== INTRO POPUP MODAL ===== */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(44, 53, 49, 0.55);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
            box-sizing: border-box;
        }

        .modal-box {
            background-color: var(--card-bg);
            border-radius: var(--border-radius);
            max-width: 440px;
            width: 100%;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(44, 53, 49, 0.2);
            border: 1px solid rgba(129, 178, 154, 0.2);
            overflow: hidden;
        }

        .modal-header {
            padding: 25px 25px 10px 25px;
        }

        .modal-header h2 {
            margin: 0;
        }

        .modal-body {
            padding: 10px 25px;
            overflow-y: auto;
            text-align: left;
            color: var(--text-main);
            font-size: 0.95rem;
            line-height: 1.7;
            white-space: pre-wrap;
        }

        .modal-footer {
            padding: 15px 25px 25px 25px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>Choose Wisely</h2>

        <!-- STEP 1: SECURITY QUESTION SECTION WITH IMAGE -->
        <div id="auth-section">
            {% if image_url %}
            <img src="{{ image_url }}" alt="Security Question Hint" class="question-image">
            {% endif %}
            <p id="question-label">{{ question }}</p>
            <div class="input-group">
                <input type="text" id="answer-input" placeholder="Enter your answer..." onkeypress="handleKeyPress(event)">
                <button onclick="verifyAnswer()">Verify Answer</button>
            </div>
            <p id="error-msg" style="color: var(--accent-color); font-size: 0.85rem; margin-top: 10px;" class="hidden">Incorrect answer. Try again.</p>
        </div>

        <!-- STEP 2: MESSAGE SELECTION SECTION (Initially Hidden) -->
        <div id="choice-section" class="hidden">
            <p id="status">Verified! Once you select a message, the server will permanently lock the other two.</p>
            
            {% if spotify_url %}
            <div class="spotify-container">
                <iframe style="border-radius:12px" src="{{ spotify_url }}" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
            </div>
            {% endif %}

            <div class="button-group">
                <button id="btn1" onclick="choose('1')">Message 1</button>
                <button id="btn2" onclick="choose('2')">Message 2</button>
                <button id="btn3" onclick="choose('3')">Message 3</button>
            </div>
            <div id="result" class="hidden"></div>
        </div>
    </div>

    <!-- INTRO POPUP: shown once, right after verification -->
    <div id="intro-modal" class="modal-overlay hidden">
        <div class="modal-box">
            <div class="modal-header">
                <h2>{{ intro_title }}</h2>
            </div>
            <div class="modal-body">{{ intro_message }}</div>
            <div class="modal-footer">
                <button onclick="closeIntro()">I've read this</button>
            </div>
        </div>
    </div>

    <script>
        let introShown = false;

        async function checkState() {
            try {
                let res = await fetch('/status?' + new Date().getTime());
                let data = await res.json();
                
                if (data.chosen_option) {
                    document.getElementById('auth-section').classList.add('hidden');
                    document.getElementById('intro-modal').classList.add('hidden');
                    document.getElementById('choice-section').classList.remove('hidden');
                    applyLock(data.chosen_option, data.message);
                } else if (data.authenticated) {
                    document.getElementById('auth-section').classList.add('hidden');
                    showIntroOrChoice();
                }
            } catch (e) {
                console.error(e);
            }
        }

        function showIntroOrChoice() {
            if (!introShown) {
                document.getElementById('intro-modal').classList.remove('hidden');
            } else {
                document.getElementById('choice-section').classList.remove('hidden');
            }
        }

        function closeIntro() {
            introShown = true;
            document.getElementById('intro-modal').classList.add('hidden');
            document.getElementById('choice-section').classList.remove('hidden');
        }

        async function verifyAnswer() {
            let answer = document.getElementById('answer-input').value;
            let res = await fetch('/verify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ answer: answer })
            });
            let data = await res.json();

            if (data.success) {
                document.getElementById('auth-section').classList.add('hidden');
                showIntroOrChoice();
            } else {
                let err = document.getElementById('error-msg');
                err.classList.remove('hidden');
                document.getElementById('answer-input').value = "";
            }
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') {
                verifyAnswer();
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
            document.querySelectorAll('#choice-section button').forEach((b, index) => {
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
            resBox.classList.remove('hidden');
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
    return render_template_string(
        HTML_TEMPLATE,
        question=SECURITY_QUESTION,
        image_url=SECURITY_IMAGE_URL,
        spotify_url=SPOTIFY_EMBED_URL,
        intro_title=INTRO_TITLE,
        intro_message=INTRO_MESSAGE
    )

@app.route('/status', methods=['GET'])
def status():
    state = get_state()
    chosen = state.get("chosen_option")
    authenticated = state.get("authenticated", False)
    if chosen:
        return jsonify({"chosen_option": chosen, "message": MESSAGES[chosen], "authenticated": True})
    return jsonify({"chosen_option": None, "authenticated": authenticated})

@app.route('/verify', methods=['POST'])
def verify():
    req_data = request.get_json()
    user_answer = req_data.get("answer", "").strip().lower()
    
    if user_answer in ACCEPTED_ANSWERS:
        state = get_state()
        state["authenticated"] = True
        save_state(state)
        return jsonify({"success": True})
    
    return jsonify({"success": False}), 400

@app.route('/choose', methods=['POST'])
def choose():
    state = get_state()
    if not state.get("authenticated", False):
        return jsonify({"success": False, "error": "Not authenticated!"}), 403
        
    if state.get("chosen_option") is not None:
        return jsonify({"success": False, "error": "A choice has already been made and locked!"}), 400
    
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
