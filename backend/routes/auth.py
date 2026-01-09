from flask import Blueprint, request, jsonify
from db import get_db_connection
from passlib.hash import bcrypt
from schemas.user import UserRegister, UserLogin
from pydantic import ValidationError
import jwt
import datetime
import os
from .auth_middleware import admin_required
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

auth_bp = Blueprint("auth", __name__)
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register user
    ---
    tags:
      - Auth
    """
    try:
        data = UserRegister(**request.json)

        conn = get_db_connection()
        cursor = conn.cursor()

        password_hash = bcrypt.hash(data.password)

        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
        """, (data.name, data.email, password_hash))

        conn.commit()

        return jsonify({"message": "User created"}), 201

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user
    ---
    tags:
      - Auth
    """
    try:
        data = UserLogin(**request.json)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s", (data.email,))
        user = cursor.fetchone()

        if not user or not bcrypt.verify(data.password, user["password_hash"]):
            return jsonify({"error": "Invalid credentials"}), 401

        token = jwt.encode(
            {
                "id": user["id"],
                "role": user["role"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({"token": token, "user": {
        "id": user["id"],
        "name": user["name"],
        "role": user["role"]
    }}), 200

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@auth_bp.route("/users", methods=["GET"])
@admin_required
def get_users():
    """
    Get users (optionally filter by role)
    ---
    tags:
      - Users
    parameters:
      - name: role
        in: query
        type: string
        required: false
    responses:
      200:
        description: List users
    """
    role = request.args.get("role")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if role:
        cursor.execute("SELECT id, name, email, role FROM users WHERE role=%s", (role,))
    else:
        cursor.execute("SELECT id, name, email, role FROM users")

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(users), 200