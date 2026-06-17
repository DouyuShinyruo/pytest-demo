from flask import Flask, request, redirect, make_response

app = Flask(__name__)

USERS = {"admin": "123456", "test": "test123"}


@app.route("/")
def index():
    return """
    <html>
    <head><title>测试平台</title></head>
    <body>
        <h1>欢迎来到测试平台</h1>
        <a href="/login">登录</a>
    </body>
    </html>
    """


@app.route("/login", methods=["GET"])
def login_page():
    return """
    <html>
    <head><title>登录</title></head>
    <body>
        <h1>用户登录</h1>
        <form id="login-form" method="POST" action="/login">
            <label for="username">用户名：</label>
            <input type="text" id="username" name="username" />
            <br/>
            <label for="password">密码：</label>
            <input type="password" id="password" name="password" />
            <br/>
            <button type="submit" id="login-btn">登录</button>
        </form>
        <div id="error-msg" style="color:red;display:none;"></div>
    </body>
    </html>
    """


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if not username or not password:
        return """
        <html><body>
        <h1>用户登录</h1>
        <form method="POST" action="/login">
            <label>用户名：</label><input type="text" name="username" /><br/>
            <label>密码：</label><input type="password" name="password" /><br/>
            <button type="submit">登录</button>
        </form>
        <div id="error-msg" style="color:red;">用户名和密码不能为空</div>
        </body></html>
        """, 400

    if username in USERS and USERS[username] == password:
        resp = make_response(redirect("/dashboard"))
        resp.set_cookie("session", f"user_{username}")
        return resp

    return """
    <html><body>
    <h1>用户登录</h1>
    <form method="POST" action="/login">
        <label>用户名：</label><input type="text" name="username" /><br/>
        <label>密码：</label><input type="password" name="password" /><br/>
        <button type="submit">登录</button>
    </form>
    <div id="error-msg" style="color:red;">用户名或密码错误</div>
    </body></html>
    """, 401


@app.route("/dashboard")
def dashboard():
    session = request.cookies.get("session")
    if not session:
        return redirect("/login")
    username = session.replace("user_", "")
    return f"""
    <html>
    <head><title>控制台</title></head>
    <body>
        <h1>欢迎, {username}!</h1>
        <p id="user-info">当前登录用户：{username}</p>
        <a href="/logout" id="logout-btn">退出</a>
    </body>
    </html>
    """


@app.route("/logout")
def logout():
    resp = make_response(redirect("/login"))
    resp.delete_cookie("session")
    return resp


if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=False)
