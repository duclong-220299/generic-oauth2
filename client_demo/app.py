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
    <h2>Client Demo Flask</h2>
    {% if userinfo %}
        <p>Đã đăng nhập: {{ userinfo['username'] }} ({{ userinfo['email'] }})</p>
        <a href="{{ url_for('logout') }}">Đăng xuất</a>
    {% else %}
        <a href="{{ url_for('login') }}">Đăng nhập với OAuth2</a>
    {% endif %}
    <hr>
    <h4>Token Response</h4>
    <pre>{{ token_data if token_data else 'Chưa có dữ liệu' }}</pre>
    <h4>Userinfo Response</h4>
    <pre>{{ userinfo if userinfo else 'Chưa có dữ liệu' }}</pre>
    <h4>Logs</h4>
    <pre>{% for log in last_logs %}{{ log }}
{% endfor %}</pre>
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
