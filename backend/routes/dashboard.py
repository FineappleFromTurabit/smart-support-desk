from flask import Blueprint, jsonify
from db import get_db_connection
from redis_client import get_cached, set_cached

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def dashboard_summary():
    """
    Dashboard ticket summary
    ---
    tags:
      - Dashboard
    responses:
      200:
        description: Ticket summary
    """
    cache_key = "dashboard:summary"

    # 1️⃣ Try cache
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached), 200

    # 2️⃣ Cache miss → compute
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM tickets
        GROUP BY status
    """)
    status_counts = cursor.fetchall()

    cursor.execute("""
        SELECT priority, COUNT(*) as count
        FROM tickets
        GROUP BY priority
    """)
    priority_counts = cursor.fetchall()

    cursor.close()
    conn.close()

    summary = {
        "by_status": status_counts,
        "by_priority": priority_counts
    }

    # 3️⃣ Store in Redis (60 sec)
    set_cached(cache_key, summary, ttl=60)

    return jsonify(summary), 200
