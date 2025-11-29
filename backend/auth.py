from flask import Blueprint, request, jsonify
from .db import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    if not username or not password:
        return jsonify({'message': 'username and password required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'username exists'}), 400
    user = User(username=username, password_hash=generate_password_hash(password), email=email)
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=2))
    return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username}})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'invalid credentials'}), 401
    token = create_access_token(identity=user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username}})
