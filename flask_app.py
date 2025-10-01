from flask import Flask, render_template_string, request, jsonify
import time

app = Flask(__name__)

# Correct credentials for brute force (CTF)
CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "security2025"

# Rate limiting store (in-memory; fine for class/demo)
failed_attempts = {}

# Wordlists
USERNAMES = [
    "admin","root","user","guest","administrator",
    "test","demo","manager","operator","supervisor",
    "developer","engineer","analyst","support","helpdesk",
    "backup","webmaster","sysadmin","dbadmin","netadmin",
    "student","teacher","professor","instructor","mentor",
    "john","jane","mike","sarah","david",
    "alice","bob","charlie","diana","edward",
    "frank","grace","henry","iris","jack",
    "kevin","laura","martin","nancy","oscar",
    "peter","quinn","rachel","steve","tina"
]

PASSWORDS = [
    "password","123456","admin123","letmein","welcome",
    "password123","admin","root","qwerty","abc123",
    "12345678","password1","welcome123","admin2024","test123",
    "user123","pass123","security","security2025","cyber123",
    "hack123","login123","access123","secret123","master123",
    "super123","power123","ultra123","mega123","hyper123",
    "dragon","shadow","phoenix","falcon","eagle",
    "tiger","lion","bear","wolf","shark",
    "matrix","vector","cipher","crypto","binary",
    "kernel","system","network","server","client"
]

MAIN_PAGE = """
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cyber Challenge Portal</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;color:#00ff00;font-family:'Courier New',monospace;min-height:100vh;
display:flex;justify-content:center;align-items:center;padding:20px}
.container{max-width:800px;border:2px solid #00ff00;padding:40px;background:rgba(0,255,0,0.05);
box-shadow:0 0 20px rgba(0,255,0,0.3)}
h1{text-align:center;margin-bottom:30px;font-size:2.0em;text-shadow:0 0 10px #00ff00}
.content{line-height:1.6}
.flag-hint{color:#00aa00;font-style:italic}
.blink{animation:blink 1s infinite}
@keyframes blink{0%,50%{opacity:1}51%,100%{opacity:0}}
</style></head>
<body>
  <div class="container">
    <h1>[STAGE 2 INITIATED]</h1>
    <div class="content">
      <p><span class="blink">&gt;</span> Welcome to the Cyber Challenge Portal</p>
      <p class="flag-hint">💡 HINT: Real hackers know how to inspect everything.</p>
      <p class="flag-hint">💡 HINT: The path forward is hidden in the source.</p>
      <p><small><!-- curl /hidden --></small></p>
    </div>
  </div>
</body>
</html>
"""

HIDDEN_PAGE = """
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hidden Resources</title>
<style>
body{background:#0a0a0a;color:#ff6600;font-family:'Courier New',monospace;padding:20px}
.container{max-width:1000px;margin:0 auto;border:2px solid #ff6600;padding:20px;background:rgba(255,102,0,0.05)}
.wordlist{background:#111;padding:10px;margin:8px 0;border-radius:4px;max-height:300px;overflow:auto}
.wordlist-item{padding:4px;border-bottom:1px solid #222}
.endpoint{color:#00ff00;font-weight:bold}
</style></head>
<body>
  <div class="container">
    <h1>[RESTRICTED ACCESS - HIDDEN RESOURCES]</h1>
    <p>Use these wordlists to brute-force <code>/login</code>.</p>
    <p>Target: <span class="endpoint">POST /login</span></p>

    <h2>📋 USERNAMES</h2>
    <div class="wordlist">
      {% for username in usernames %}
      <div class="wordlist-item">{{ username }}</div>
      {% endfor %}
    </div>

    <h2>🔑 PASSWORDS</h2>
    <div class="wordlist">
      {% for password in passwords %}
      <div class="wordlist-item">{{ password }}</div>
      {% endfor %}
    </div>

    <p>Plain text wordlists: <code>/wordlists.txt</code></p>
  </div>
</body>
</html>
"""

@app.route('/')
def index():
    return MAIN_PAGE

@app.route('/hidden')
def hidden():
    return render_template_string(HIDDEN_PAGE, usernames=USERNAMES, passwords=PASSWORDS)

@app.route('/wordlists.txt')
def wordlists_txt():
    u = "\n".join(USERNAMES)
    p = "\n".join(PASSWORDS)
    txt = f"---USERNAMES---\n{u}\n\n---PASSWORDS---\n{p}\n"
    return txt, 200, {'Content-Type': 'text/plain; charset=utf-8'}

def get_client_ip():
    xff = request.headers.get('X-Forwarded-For','')
    if xff:
        return xff.split(',')[0].strip()
    return request.remote_addr or 'unknown'

@app.route('/login', methods=['POST'])
def login():
    client_ip = get_client_ip()
    t = time.time()

    # reset window after 60s
    if client_ip in failed_attempts:
        last, count = failed_attempts[client_ip]
        if t - last > 60:
            failed_attempts[client_ip] = [t, 0]

    data = request.get_json(silent=True) or request.form or {}
    username = data.get('username','')
    password = data.get('password','')

    if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
        if client_ip in failed_attempts:
            del failed_attempts[client_ip]
        return jsonify({
            "status":"success",
            "FLAG2":"CTF{BR0T3_F0RC3_M4ST3R_H4CK3R}",
            "machine": {
                "username":"ctfuser",
                "password":"Cyb3rS3c2024!",
                "ip":"192.168.1.100",
                "port":22
            }
        }), 200

    # track fail
    if client_ip not in failed_attempts:
        failed_attempts[client_ip] = [t, 1]
    else:
        failed_attempts[client_ip][1] += 1

    return jsonify({"status":"error","message":"Invalid credentials"}), 401

# keep local run guard for convenience, gunicorn will import app for production
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
