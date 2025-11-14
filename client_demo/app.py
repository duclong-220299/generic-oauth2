from flask import Flask, redirect, request, session, url_for, render_template_string
import requests

import logging

app = Flask(__name__)
app.secret_key = 'demo_secret_key'
logging.basicConfig(level=logging.INFO)

OAUTH2_SERVER = 'http://localhost:8000'
CLIENT_ID = 'NkvUmwSOTjnTddjaHEBmi_HfHyTo-3B_1Ni8KnZhDW8'
CLIENT_SECRET = 'UPU-xWoRRUkPpWKo1NB493AXmWjxwuX2wf-VcDyh9a0'
REDIRECT_URI = 'http://localhost:3000/oauth2/callback'
SCOPES = 'profile'

@app.route('/')
def home():
    userinfo = session.get('userinfo')
    token_data = session.get('token_data')
    last_logs = session.get('last_logs', [])
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Client Demo Flask OAuth2</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
        <style>
            body {
                background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
                min-height: 100vh;
            }
            .card {
                max-width: 700px;
                margin: 40px auto;
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
                border: none;
            }
            .pre-scroll {
                max-height: 250px;
                overflow-y: auto;
                background: #212529;
                color: #f8f9fa;
                padding: 1em;
                border-radius: 8px;
                font-size: 0.95em;
            }
            .copy-btn {
                float: right;
                margin-top: -8px;
            }
            .gradient-header {
                background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
                color: #fff;
                border-radius: 18px 18px 0 0;
                padding: 32px 0 16px 0;
                box-shadow: 0 4px 16px rgba(106,17,203,0.08);
            }
            .icon-status {
                font-size: 2em;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
        <div class="card shadow">
            <div class="gradient-header text-center">
                <i class="fa-solid fa-shield-halved fa-bounce"></i>
                <h2 class="mb-2 mt-2">Client Demo Flask OAuth2</h2>
            </div>
            <div class="card-body">
                {% if userinfo %}
                    <div class="alert alert-success text-start">
                        <i class="fa-solid fa-circle-check text-success icon-status"></i>
                        <strong>Đã đăng nhập:</strong> {{ userinfo['username'] }}<br>
                        <strong>Email:</strong> {{ userinfo['email'] }}
                    </div>
                    <a href="{{ url_for('logout') }}" class="btn btn-danger mb-3"><i class="fa-solid fa-right-from-bracket"></i> Đăng xuất</a>
                {% else %}
                    <div class="alert alert-warning"><i class="fa-solid fa-circle-exclamation text-warning icon-status"></i> Bạn chưa đăng nhập.</div>
                    <a href="{{ url_for('login') }}" class="btn btn-success mb-3"><i class="fa-solid fa-right-to-bracket"></i> Đăng nhập với OAuth2</a>
                {% endif %}
                <hr>
                <div class="mb-4">
                    <h5 class="mt-4 d-inline">Token Response</h5>
                    {% if token_data %}
                        <button class="btn btn-sm btn-outline-light copy-btn" onclick="copyToken()"><i class="fa-regular fa-copy"></i> Copy</button>
                    {% endif %}
                    <div class="pre-scroll" id="token-box">{{ token_data if token_data else 'Chưa có dữ liệu' }}</div>
                </div>
                <div class="mb-4">
                    <h5 class="mt-4">Userinfo Response</h5>
                    <div class="pre-scroll">{{ userinfo if userinfo else 'Chưa có dữ liệu' }}</div>
                </div>
                <div class="mb-4">
                    <h5 class="mt-4">Logs</h5>
                    <div class="pre-scroll">{% for log in last_logs %}{{ log }}<br>{% endfor %}</div>
                </div>
            </div>
        </div>
        <footer class="text-center mt-4 mb-2 text-muted">&copy; {{ 2025 }} <i class="fa-solid fa-bolt"></i> Client Demo Flask OAuth2</footer>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
        function copyToken() {
            var tokenBox = document.getElementById('token-box');
            var text = tokenBox.innerText;
            navigator.clipboard.writeText(text);
            alert('Đã copy token!');
        }
        </script>
    </body>
    </html>
    ''', userinfo=userinfo, token_data=token_data, last_logs=last_logs)

@app.route('/login')
def login():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'response_type': 'code',
        'state': 'demo123'
    }
    auth_url = f"{OAUTH2_SERVER}/oauth2/authorize?" + '&'.join([f"{k}={v}" for k,v in params.items()])
    return redirect(auth_url)

@app.route('/oauth2/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    logs = []
    if not code:
        logs.append('Không nhận được mã xác nhận')
        session['last_logs'] = logs
        return 'Không nhận được mã xác nhận', 400
    # Lấy access token
    token_url = f"{OAUTH2_SERVER}/oauth2/token"
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    resp = requests.post(token_url, data=data)
    logs.append(f"Token request: {data}")
    logs.append(f"Token response [{resp.status_code}]: {resp.text}")
    if resp.status_code != 200:
        session['last_logs'] = logs
        return f'Lỗi lấy token: {resp.text}', 400
    token_data = resp.json()
    session['token_data'] = token_data
    access_token = token_data.get('access_token')
    # Lấy thông tin user
    userinfo_url = f"{OAUTH2_SERVER}/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    userinfo_resp = requests.get(userinfo_url, headers=headers)
    logs.append(f"Userinfo request: {headers}")
    logs.append(f"Userinfo response [{userinfo_resp.status_code}]: {userinfo_resp.text}")
    if userinfo_resp.status_code == 200:
        session['userinfo'] = userinfo_resp.json()
    else:
        session['userinfo'] = None
    session['last_logs'] = logs
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)
