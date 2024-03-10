#!/usr/bin/python3

from api.blueprint import app_views, auth
from flask import request, jsonify
from model.user import User
from model.usersession import UserSession
from model import storage

@app_views.route('/user/<user_id>', methods=['GET', 'PUT'], strict_slashes=False)
@auth.login_required
def get_user(user_id):
    # if request.method == 'GET':
    if user_id == 'me':
        user = auth.current_user()
    else:
        user = storage.get("User", user_id)
    if not user:
        return jsonify("User not found"), 404
    
    if request.method == 'GET':
        return jsonify(user.to_dict())
    
    elif request.method == 'PUT':
        if not request.json:
            return jsonify("Not a valid json"), 400
        data = request.get_json()
        
        for key, val in data.items():
            setattr(user, key, val)
        user.save()
        return jsonify("User updated successfully")

@app_views.route('/users', methods=['POST'], strict_slashes=False)
def create_user():
    if not request.json:
        return jsonify({'msg': "Data must be a valid json",'code': 400}), 400
    data = request.get_json()
    required_attr = ['email', 'password', 'username']
    for attr in required_attr:
        if attr not in data:
            return jsonify({'msg': f"{attr} is required to create User", 'code': 400}), 400
    model = User(**data)
    model.save()
    session = UserSession(user_id=model.id)
    session.save()
    return jsonify({"msg": "User created successfully", 'code': 200,
                    'session_id': session.id}), 200

@app_views.route('/auth/login', methods=['POST'], strict_slashes=False)
def login():
    if not request.json:
        return jsonify("Not a valid json"), 400
    
    data = request.get_json()
    
    if "username" not in data or "password" not in data:
        return jsonify("Username or password missing"), 400
    
    username = data.get("username")
    password = data.get("password")
    user = storage.search("User", username=username)
    if not user:
        return jsonify("No user with this username found"), 400
    if user[0].password != password:
        return jsonify("Password is incorrect"), 400
    
    previous_sessions = storage.search("UserSession", user_id=user[0].id)
    for sess in previous_sessions:
        sess.delete()
    session = UserSession(user_id=user[0].id)
    session.save()
    return jsonify({"msg": f"Welcome back {user[0].username}", "session_id": session.id,
                    "has_bot": user[0].has_bot})

# @app_views.route('/users/<')