from flask import Flask, render_template_string, request, jsonify
import time

app = Flask(__name__)

# Correct credentials for brute force
CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "security2024"

# Rate limiting - track failed attempts
failed_attempts = {}

# Username wordlist (50 usernames)
USERNAMES = [
    "admin", "root", "user", "guest", "administrator",
    "test", "demo", "manager", "operator", "supervisor",
    "developer", "engineer", "analyst", "support", "helpdesk",
    "backup", "webmaster", "sysadmin", "dbadmin", "netadmin",
    "student", "teacher", "professor", "instructor", "mentor",
    "john", "jane", "mike", "sarah", "david",
    "alice", "bob", "charlie", "diana", "edward",
    "frank", "grace", "henry", "iris", "jack",
    "kevin", "laura", "martin", "nancy", "oscar",
    "peter", "quinn", "rachel", "steve", "tina"
]

# Password wordlist (50 passwords)
PASSWORDS = [
    "password", "123456", "admin123", "letmein", "welcome",
    "password123", "admin", "root", "qwerty", "abc123",
    "12345678", "password1", "welcome123", "admin2024", "test123",
    "user123", "pass123", "security", "security2024", "cyber123",
    "hack123", "login123", "access123", "secret123", "master123",
    "super123", "power123", "ultra123", "mega123", "hyper123",
    "dragon", "shadow", "phoenix", "falcon", "eagle",
    "tiger", "lion", "bear", "wolf", "shark",
    "matrix", "vector", "cipher", "crypto", "binary",
    "kernel", "system", "network", "server", "client"
]

# Main page HTML
MAIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Challenge Portal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #0a0a0a;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            border: 2px solid #00ff00;
            padding: 40px;
            background: rgba(0, 255, 0, 0.05);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ff00;
        }
        .ascii-art {
            text-align: center;
            margin-bottom: 30px;
            font-size: 0.8em;
            line-height: 1.2;
        }
        .content {
            line-height: 1.8;
        }
        .content p {
            margin-bottom: 15px;
        }
        .flag-hint {
            color: #00aa00;
            font-style: italic;
        }
        .blink {
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="ascii-art">
    _____ _____  _____   _____ _           _ _                       
   / ____|_   _||  __ \ / ____| |         | | |                      
  | |      | |  | |__) | |    | |__   __ _| | | ___ _ __   __ _  ___ 
  | |      | |  |  _  /| |    | '_ \ / _` | | |/ _ \ '_ \ / _` |/ _ \
  | |____ _| |_ | | \ \| |____| | | | (_| | | |  __/ | | | (_| |  __/
   \_____|_____||_|  \_\\_____|_| |_|\__,_|_|_|\___|_| |_|\__, |\___|
                                                            __/ |     
                                                           |___/      
        </div>
        
        <h1>[STAGE 2 INITIATED]</h1>
        
        <div class="content">
            <p><span class="blink">&gt;</span> Welcome to the Cyber Challenge Portal</p>
            <p><span class="blink">&gt;</span> You have successfully completed Stage 1</p>
            <p><span class="blink">&gt;</span> Your mission continues...</p>
            <br>
            <p class="flag-hint">💡 HINT: Real hackers know how to inspect everything.</p>
            <p class="flag-hint">💡 HINT: The path forward is hidden in the source.</p>
            <br>
            <p><span class="blink">&gt;</span> Status: AUTHENTICATED</p>
            <p><span class="blink">&gt;</span> Clearance Level: BASIC</p>
            <p><span class="blink">&gt;</span> Next Objective: FIND THE HIDDEN PATH</p>
        </div>
    </div>
    
    <!-- To access hidden resources, use: curl http://Adaegy.pythonanywhere.com/hidden -->
</body>
</html>
"""

# Hidden page HTML
HIDDEN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hidden Resources</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #0a0a0a;
            color: #ff6600;
            font-family: 'Courier New', monospace;
            padding: 40px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            border: 2px solid #ff6600;
            padding: 30px;
            background: rgba(255, 102, 0, 0.05);
        }
        h1 {
            color: #ff6600;
            text-shadow: 0 0 10px #ff6600;
            margin-bottom: 20px;
        }
        h2 {
            color: #ff8833;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        .wordlist {
            background: #1a1a1a;
            border: 1px solid #ff6600;
            padding: 20px;
            margin: 10px 0;
            max-height: 300px;
            overflow-y: auto;
        }
        .wordlist-item {
            padding: 5px;
            border-bottom: 1px solid #333;
        }
        .hint {
            background: rgba(255, 102, 0, 0.1);
            padding: 15px;
            margin: 20px 0;
            border-left: 4px solid #ff6600;
        }
        .endpoint {
            color: #00ff00;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>[RESTRICTED ACCESS - HIDDEN RESOURCES]</h1>
        
        <div class="hint">
            <p><strong>⚠️ OBJECTIVE:</strong></p>
            <p>Use these wordlists to perform a brute force attack on the login endpoint.</p>
            <p><strong>Target:</strong> <span class="endpoint">POST http://Adaegy.pythonanywhere.com/login</span></p>
            <p><strong>Method:</strong> Write a Python script to test combinations</p>
            <p><strong>Parameters:</strong> username, password</p>
        </div>
        
        <h2>📋 USERNAME WORDLIST (50 entries)</h2>
        <div class="wordlist" id="usernames">
            {% for username in usernames %}
            <div class="wordlist-item">{{ username }}</div>
            {% endfor %}
        </div>
        
        <h2>🔑 PASSWORD WORDLIST (50 entries)</h2>
        <div class="wordlist" id="passwords">
            {% for password in passwords %}
            <div class="wordlist-item">{{ password }}</div>
            {% endfor %}
        </div>
        
        <div class="hint">
            <p><strong>💡 TIPS:</strong></p>
            <p>• Save these wordlists to text files</p>
            <p>• Use the requests library in Python</p>
            <p>• Send POST requests with username and password</p>
            <p>• Look for successful response (status 200 with FLAG2)</p>
            <p>• Failed attempts return status 401</p>
        </div>
    </div>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    return MAIN_PAGE

@app.route('/hidden')
def hidden():
    return render_template_string(HIDDEN_PAGE, usernames=USERNAMES, passwords=PASSWORDS)

@app.route('/login', methods=['POST'])
def login():
    # Get client IP for rate limiting
    client_ip = request.remote_addr
    
    # Simple rate limiting (optional - can remove if causes issues)
    current_time = time.time()
    if client_ip in failed_attempts:
        last_attempt_time, count = failed_attempts[client_ip]
        # Reset counter after 60 seconds
        if current_time - last_attempt_time > 60:
            failed_attempts[client_ip] = [current_time, 0]
    
    # Get credentials from request
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '')
    password = data.get('password', '')
    
    # Check credentials
    if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
        # Clear failed attempts
        if client_ip in failed_attempts:
            del failed_attempts[client_ip]
        
        # Return FLAG2 and machine credentials
        return jsonify({
            "status": "success",
            "message": "Authentication successful!",
            "FLAG2": "CTF{BR0T3_F0RC3_M4ST3R_H4CK3R}",
            "next_stage": {
                "description": "SSH Machine Access",
                "credentials": {
                    "username": "ctfuser",
                    "password": "Cyb3rS3c2024!",
                    "ip": "192.168.1.100",
                    "port": 22
                },
                "instructions": "Use these credentials to SSH into the machine and find FLAG3"
            }
        }), 200
    else:
        # Track failed attempt
        if client_ip not in failed_attempts:
            failed_attempts[client_ip] = [current_time, 1]
        else:
            failed_attempts[client_ip][1] += 1
        
        return jsonify({
            "status": "error",
            "message": "Invalid credentials"
        }), 401

if __name__ == '__main__':
    app.run(debug=True)
