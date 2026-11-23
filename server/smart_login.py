from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
from werkzeug.security import check_password_hash
from auth import db
from extensions import limiter


smart_login_bp = Blueprint('smart_login', __name__, url_prefix='/admin')


@smart_login_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    admin_result = None  # Initialize to avoid UnboundLocalError
    rep_result = None    # Initialize to avoid UnboundLocalError

    try:
        with db.engine.connect() as conn:
            # 1. Check Admin
            admin_result = conn.execute(
                text("SELECT * FROM admins WHERE username = :username"),
                {"username": username}
            ).fetchone()

            if admin_result and check_password_hash(
                admin_result._mapping["password_hash"], password
            ):
                session.clear()
                session["admin_id"] = admin_result._mapping["admin_id"]

                return jsonify({
                    "status": "success",
                    "role": "admin",
                    "message": "Admin login successful"
                }), 200

            # 2. Check Customer Rep
            rep_result = conn.execute(
                text("SELECT * FROM customer_reps WHERE username = :username"),
                {"username": username}
            ).fetchone()

            if rep_result and check_password_hash(
                rep_result._mapping["password_hash"], password
            ):
                session.clear()
                session["rep_id"] = rep_result._mapping["rep_id"]

                return jsonify({
                    "status": "success",
                    "role": "customer_rep",
                    "message": "Customer representative login successful"
                }), 200

    except Exception:
        return jsonify({"status": "error", "message": "Login failed"}), 500

    # 3. If nothing found
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401
