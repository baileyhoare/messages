from flask import Flask, render_template_string, jsonify, request
import json
import os
import requests

app = Flask(__name__)

STATE_FILE = "state.json"

# ==========================================
# NOTIFICATIONS
# ==========================================
# Set to False when you're ready to send this to the real recipient.
# While True, no notifications are sent - safe for testing.
TESTING_MODE = True

# A webhook URL that receives a POST with a JSON body like {"content": "..."}.
# Easiest free option: https://ntfy.sh - pick a private topic name, e.g.
#   NOTIFY_WEBHOOK_URL = "https://ntfy.sh/your-private-topic-name-here"
# Discord and Slack "incoming webhook" URLs also work.
NOTIFY_WEBHOOK_URL = ""

def send_notification(message):
    if TESTING_MODE or not NOTIFY_WEBHOOK_URL:
        return
    try:
        if "ntfy.sh" in NOTIFY_WEBHOOK_URL:
            requests.post(NOTIFY_WEBHOOK_URL, data=message.encode("utf-8"), timeout=5)
        else:
            # Discord/Slack-style webhook
            requests.post(NOTIFY_WEBHOOK_URL, json={"content": message, "text": message}, timeout=5)
    except Exception:
        pass  # Never let a failed notification break the site

# ==========================================
# CONFIGURATION
# ==========================================
SECURITY_QUESTION = "What is this guy's name?"
# Replace with your direct image URL, or leave as "" for text-only
SECURITY_IMAGE_URL = "/static/lorentz.jpg"

ACCEPTED_ANSWERS = ["Lorentz", "lorentz"]

# INTRO MESSAGE - shown as a scrollable, typewritten popup right after the security question is passed
INTRO_TITLE = "Hey Char"
INTRO_MESSAGE = """

I made a website. It took a while, but I knew I was going to wait until you had left Canada before sending it to you (which I think has 
happened). You were always great at making fun websites for me. I had to build a dedicated front- and back-end because there are a couple
of tricks which I will explain in a minute. Simply put, I wanted to reach out, with some of my thoughts over the last couple of months. I knew
what I wanted to say, but not how to say it, and ended up drafting a couple of versions. I realised that it was because I had no gauge as to
how you were doing, and didn't want to upset you or come across in the wrong way, for why I couldn't get the message quite right. So, I built
this website, and you can choose. Each message is similar in content, but with a bit of a different tone, and places emphasis on different
things. You will choose one message to read, and the other two will be locked away. As far as I know, there is no way to unlock the other two
messages once you choose, so be careful.

I thought about adding some fun easter eggs, but didn't want to overdo it. A nice colour scheme of sage green and sunset orange, along with
the security question (well done on passing) should do it.

The first message is long, intellectual, and deeply reflective. Choose it if you want a deep apology, and true acceptance of where we went wrong.

The second message is shorter and more emotionally vulnerable. Choose it if 

The final message is a message of closure. Choose it if you are ready to move on.

While I made the website as a fun way to get you this message, provide you agency, and not force you into a situation where you felt pressure
to reply, I recognise this is not exactly 'fun', and you may have mixed emotions regarding everything. It is worth saying that I am completely
at peace with the idea that you may not want to reply, and rest assured that I will not hassle you any further. It was bugging me greatly, 
everything that was left unsaid, and we now have a way to remediate that issue.

I really don't know how this will go down - it is quite daunting reaching out and being pretty vulnerable on here. All I know is that things
ended so quickly, and I wanted to address a couple of things for good. Just to let you know, this website will automatically be taken down 24
hours after you choose to open one of the messages. If you wish to respond, take whatever time you need. Obviously you can copy/paste the
messages, and do whatever you wish with what I have written, but it would be nice to keep this between us if possible.

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
            color: var(--text-main);
            text-align: center;
            padding: 20px;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
            background-color: var(--bg-color);
            position: relative;
            overflow: hidden;
        }

        #particle-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: block;
            z-index: 0;
        }

        .card {
            position: relative;
            z-index: 1;
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

        .envelope-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
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

        .envelope-btn:hover:not(:disabled) {
            background-color: var(--accent-hover);
        }

        .envelope-btn:active:not(:disabled) {
            transform: scale(0.98);
        }

        .envelope-btn:disabled {
            background-color: var(--locked-bg);
            color: var(--locked-text);
            cursor: not-allowed;
        }

        .envelope-btn svg {
            flex-shrink: 0;
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

        button.secondary {
            background-color: transparent;
            color: var(--text-muted);
            border: 1px solid #cbd5e1;
        }

        button.secondary:hover:not(:disabled) {
            background-color: #f1f5f2;
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

        /* ===== MODAL (shared by intro + confirmation) ===== */
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
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

    </style>
</head>
<body>
    <canvas id="particle-canvas"></canvas>

    <div class="card">
        <h2>Security Check</h2>

        <!-- STEP 1: SECURITY QUESTION SECTION WITH IMAGE -->
        <div id="auth-section">
            {% if image_url %}
            <img src="{{ image_url }}" alt="Security Question Hint" class="question-image">
            {% endif %}
            <p id="question-label">{{ question }}</p>
            <div class="input-group">
                <input type="text" id="answer-input" placeholder="Enter your answer..." onkeypress="handleKeyPress(event)">
                <button onclick="playClick(); verifyAnswer()">Verify Answer</button>
            </div>
            <p id="error-msg" style="color: var(--accent-color); font-size: 0.85rem; margin-top: 10px;" class="hidden">Incorrect answer. Try again.</p>
        </div>

        <!-- STEP 2: MESSAGE SELECTION SECTION (Initially Hidden) -->
        <div id="choice-section" class="hidden">
            <p id="status">Verified! Once you select a message, the server will permanently lock the other two.</p>

            <div class="button-group">
                <button id="btn1" class="envelope-btn" onclick="playClick(); requestChoice('1')">
                    <svg id="env-icon-1" width="28" height="20" viewBox="0 0 28 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="1" y="1" width="26" height="18" rx="2" stroke="white" stroke-width="1.5"/>
                        <path d="M2 2L14 12L26 2" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="20" cy="6" r="2.5" fill="white"/>
                    </svg>
                    <span>Message 1</span>
                </button>
                <button id="btn2" class="envelope-btn" onclick="playClick(); requestChoice('2')">
                    <svg id="env-icon-2" width="28" height="20" viewBox="0 0 28 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="1" y="1" width="26" height="18" rx="2" stroke="white" stroke-width="1.5"/>
                        <path d="M2 2L14 12L26 2" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="20" cy="6" r="2.5" fill="white"/>
                    </svg>
                    <span>Message 2</span>
                </button>
                <button id="btn3" class="envelope-btn" onclick="playClick(); requestChoice('3')">
                    <svg id="env-icon-3" width="28" height="20" viewBox="0 0 28 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="1" y="1" width="26" height="18" rx="2" stroke="white" stroke-width="1.5"/>
                        <path d="M2 2L14 12L26 2" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="20" cy="6" r="2.5" fill="white"/>
                    </svg>
                    <span>Message 3</span>
                </button>
            </div>
            <div id="result" class="hidden"></div>
        </div>
    </div>

    <!-- INTRO POPUP: shown once, right after verification. Typewriter effect. -->
    <div id="intro-modal" class="modal-overlay hidden">
        <div class="modal-box">
            <div class="modal-header">
                <h2>{{ intro_title }}</h2>
            </div>
            <div class="modal-body" id="intro-body"></div>
            <div class="modal-footer">
                <button id="intro-continue-btn" onclick="playClick(); closeIntro()" disabled>I've read this</button>
            </div>
        </div>
    </div>

    <!-- CONFIRMATION RITUAL: replaces the default browser confirm() -->
    <div id="confirm-modal" class="modal-overlay hidden">
        <div class="modal-box">
            <div class="modal-header">
                <h2>Are you sure?</h2>
            </div>
            <div class="modal-body">
                <p style="margin:0;">Once you choose, the other two messages lock forever. There's no way back from here.</p>
            </div>
            <div class="modal-footer">
                <button id="confirm-yes-btn" onclick="playClick(); confirmChoice()" disabled>Yes, I'm sure</button>
                <button class="secondary" onclick="playClick(); cancelChoice()">Wait, not yet</button>
            </div>
        </div>
    </div>

    <script>
        // ---------- Interactive particle field ----------
        (function() {
            const canvas = document.getElementById('particle-canvas');
            if (!canvas) { console.error('particle-canvas element not found'); return; }
            const ctx = canvas.getContext('2d');
            if (!ctx) { console.error('2D canvas context not available'); return; }
            let width, height, particles;
            const colors = ['#81b29a', '#e07a5f', '#a8c4b4', '#eba488'];
            const mouse = { x: -9999, y: -9999, active: false };

            function resize() {
                width = canvas.width = window.innerWidth;
                height = canvas.height = window.innerHeight;
            }

            function initParticles() {
                const count = Math.min(140, Math.floor((width * height) / 9000));
                particles = [];
                for (let i = 0; i < count; i++) {
                    particles.push({
                        x: Math.random() * width,
                        y: Math.random() * height,
                        vx: (Math.random() - 0.5) * 0.4,
                        vy: (Math.random() - 0.5) * 0.4,
                        r: Math.random() * 2.5 + 2,
                        color: colors[Math.floor(Math.random() * colors.length)]
                    });
                }
            }

            function step() {
                ctx.clearRect(0, 0, width, height);

                for (let p of particles) {
                    // Gentle drift
                    p.x += p.vx;
                    p.y += p.vy;

                    // Wrap around edges
                    if (p.x < -10) p.x = width + 10;
                    if (p.x > width + 10) p.x = -10;
                    if (p.y < -10) p.y = height + 10;
                    if (p.y > height + 10) p.y = -10;

                    // Mouse interaction: gently repel nearby particles
                    if (mouse.active) {
                        const dx = p.x - mouse.x;
                        const dy = p.y - mouse.y;
                        const dist = Math.sqrt(dx * dx + dy * dy);
                        const radius = 130;
                        if (dist < radius && dist > 0.01) {
                            const force = (1 - dist / radius) * 1.8;
                            p.x += (dx / dist) * force;
                            p.y += (dy / dist) * force;
                        }
                    }

                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = p.color;
                    ctx.globalAlpha = 0.8;
                    ctx.fill();
                }

                // Draw connecting lines between nearby particles
                ctx.globalAlpha = 1;
                for (let i = 0; i < particles.length; i++) {
                    for (let j = i + 1; j < particles.length; j++) {
                        const a = particles[i], b = particles[j];
                        const dx = a.x - b.x, dy = a.y - b.y;
                        const dist = Math.sqrt(dx * dx + dy * dy);
                        if (dist < 130) {
                            ctx.beginPath();
                            ctx.moveTo(a.x, a.y);
                            ctx.lineTo(b.x, b.y);
                            ctx.strokeStyle = 'rgba(129, 178, 154, ' + (0.35 * (1 - dist / 130)) + ')';
                            ctx.lineWidth = 1.2;
                            ctx.stroke();
                        }
                    }
                }

                requestAnimationFrame(step);
            }

            window.addEventListener('resize', () => { resize(); initParticles(); });
            window.addEventListener('mousemove', (e) => {
                mouse.x = e.clientX;
                mouse.y = e.clientY;
                mouse.active = true;
            });
            window.addEventListener('mouseleave', () => { mouse.active = false; });
            window.addEventListener('touchmove', (e) => {
                if (e.touches.length > 0) {
                    mouse.x = e.touches[0].clientX;
                    mouse.y = e.touches[0].clientY;
                    mouse.active = true;
                }
            }, { passive: true });
            window.addEventListener('touchend', () => { mouse.active = false; });

            resize();
            initParticles();
            step();
        })();

        let introShown = false;
        let pendingChoice = null;

        // ---------- Sound effect (Web Audio API, no external file needed) ----------
        let audioCtx = null;
        function playClick() {
            try {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(520, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(280, audioCtx.currentTime + 0.09);
                gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.12);
                osc.connect(gain).connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.12);
            } catch (e) {
                // Audio not available - fail silently
            }
        }

        // ---------- Show intro text immediately (no typewriter) ----------
        function typewriteIntro() {
            const el = document.getElementById('intro-body');
            const btn = document.getElementById('intro-continue-btn');
            el.textContent = {{ intro_message|tojson }};
            btn.disabled = false;
        }

        async function checkState() {
            try {
                let res = await fetch('/status?' + new Date().getTime());
                let data = await res.json();
                
                if (data.chosen_option) {
                    document.getElementById('auth-section').classList.add('hidden');
                    document.getElementById('intro-modal').classList.add('hidden');
                    document.getElementById('confirm-modal').classList.add('hidden');
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
                typewriteIntro();
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

        // ---------- Confirmation ritual (replaces browser confirm()) ----------
        function requestChoice(option) {
            pendingChoice = option;
            const yesBtn = document.getElementById('confirm-yes-btn');
            yesBtn.disabled = true;
            document.getElementById('confirm-modal').classList.remove('hidden');

            // 5 second countdown before the confirm button becomes clickable
            let secondsLeft = 5;
            yesBtn.innerText = `Yes, I'm sure (${secondsLeft})`;
            const countdown = setInterval(() => {
                secondsLeft -= 1;
                if (secondsLeft > 0) {
                    yesBtn.innerText = `Yes, I'm sure (${secondsLeft})`;
                } else {
                    clearInterval(countdown);
                    yesBtn.innerText = "Yes, I'm sure";
                    yesBtn.disabled = false;
                }
            }, 1000);
        }

        function cancelChoice() {
            pendingChoice = null;
            document.getElementById('confirm-yes-btn').innerText = "Yes, I'm sure";
            document.getElementById('confirm-modal').classList.add('hidden');
        }

        async function confirmChoice() {
            if (!pendingChoice) return;
            const option = pendingChoice;
            document.getElementById('confirm-modal').classList.add('hidden');

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
            pendingChoice = null;
        }

        function applyLock(chosen, msg) {
            document.querySelectorAll('#choice-section .envelope-btn').forEach((b, index) => {
                b.disabled = true;
                const num = index + 1;
                const label = b.querySelector('span');
                const icon = b.querySelector('svg');

                if ((num).toString() === chosen) {
                    b.style.backgroundColor = "var(--accent-active)";
                    label.textContent = `Message ${chosen} (Opened)`;
                    // Open envelope icon: flap open, letter peeking out
                    icon.innerHTML = `
                        <path d="M2 6L14 14L26 6" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <rect x="6" y="1" width="16" height="12" rx="1" stroke="white" stroke-width="1.5" fill="none"/>
                        <rect x="1" y="6" width="26" height="13" rx="2" stroke="white" stroke-width="1.5" fill="none"/>
                    `;
                } else {
                    label.textContent = `Message ${num} (Locked)`;
                    // Sealed envelope with small lock dot
                    icon.innerHTML = `
                        <rect x="1" y="1" width="26" height="18" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/>
                        <path d="M2 2L14 12L26 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <circle cx="20" cy="6" r="2.5" fill="currentColor"/>
                    `;
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
    send_notification("🔗 The link has been accessed.")
    return render_template_string(
        HTML_TEMPLATE,
        question=SECURITY_QUESTION,
        image_url=SECURITY_IMAGE_URL,
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
        send_notification(f"💌 A choice has been made: Message {choice} was opened.")
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
