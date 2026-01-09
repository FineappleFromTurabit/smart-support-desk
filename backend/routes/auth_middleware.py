from flask import request, jsonify
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def auth_required(f):
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth:
            return jsonify({"error": "Missing token"}), 401

        token = auth.replace("Bearer ", "")
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = user
        except:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


def admin_required(f):
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth:
            return jsonify({"error": "Missing token"}), 401

        token = auth.replace("Bearer ", "")
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if user["role"] != "admin":
                return jsonify({"error": "Admin only"}), 403
            request.user = user
        except:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper