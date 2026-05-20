from flask import Flask, request, jsonify

app = Flask(__name__)

# 内存数据库
users_db = {}
next_id = 1


@app.route("/api/users", methods=["GET"])
def list_users():
    """获取用户列表"""
    return jsonify(list(users_db.values()))


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """获取单个用户"""
    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify(user)


@app.route("/api/users", methods=["POST"])
def create_user():
    """创建用户"""
    global next_id
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({"error": "用户名不能为空"}), 400

    user = {
        "id": next_id,
        "name": data["name"],
        "email": data.get("email", ""),
    }
    users_db[next_id] = user
    next_id += 1
    return jsonify(user), 201


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """更新用户"""
    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    data = request.get_json()
    if data.get("name"):
        user["name"] = data["name"]
    if data.get("email"):
        user["email"] = data["email"]

    users_db[user_id] = user
    return jsonify(user)


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """删除用户"""
    if user_id not in users_db:
        return jsonify({"error": "用户不存在"}), 404

    del users_db[user_id]
    return jsonify({"message": "删除成功"})


@app.route("/api/reset", methods=["POST"])
def reset():
    """重置数据（测试用）"""
    global next_id
    users_db.clear()
    next_id = 1
    return jsonify({"message": "重置成功"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
