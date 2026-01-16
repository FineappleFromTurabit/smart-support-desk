from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from schemas.ticket import TicketCreate
from db import get_db_connection
from redis_client import delete_cached 
from routes.auth_middleware import auth_required, admin_required

tickets_bp = Blueprint("tickets", __name__)
@tickets_bp.route("/tickets", methods=["POST"])
def create_ticket():
    """
    Create a new support ticket
    ---
    tags:
      - Tickets
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - customer_id
            - title
            - priority
          properties:
            customer_id:
              type: integer
              example: 1
            title:
              type: string
              example: Login not working
            description:
              type: string
              example: User cannot log in since yesterday
            priority:
              type: string
              enum: [LOW, MEDIUM, HIGH]
    responses:
      201:
        description: Ticket created
      400:
        description: Validation error
      404:
        description: Customer not found
      500:
        description: Internal server error
    """
    try:
        data = TicketCreate(**request.json)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1️⃣ Check customer exists
        cursor.execute(
            "SELECT id FROM customers WHERE id = %s",
            (data.customer_id,)
        )
        customer = cursor.fetchone()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # 2️⃣ Insert ticket
        cursor.execute("""
            INSERT INTO tickets (customer_id, title, description, priority,assigned_to)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data.customer_id,
            data.title,
            data.description,
            data.priority,
            data.assigned_to
        ))

        conn.commit()   #  ticket is now saved

        # INVALIDATE DASHBOARD CACHE (THIS IS THE LINE)
        delete_cached("dashboard:summary")

        return jsonify({"message": "Ticket created"}), 201

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
            conn.close()

@tickets_bp.route("/tickets", methods=["GET"])
def get_tickets():
    """
    Get tickets with optional filters
    ---
    tags:
      - Tickets
    parameters:
      - name: status
        in: query
        type: string
        enum: [OPEN, IN_PROGRESS, CLOSED]
      - name: priority
        in: query
        type: string
        enum: [LOW, MEDIUM, HIGH]
      - name: customer_id
        in: query
        type: integer
    responses:
      200:
        description: List of tickets
      400:
        description: Invalid query parameters
      500:
        description: Internal server error
    """
    try:
        status = request.args.get("status")
        priority = request.args.get("priority")
        customer_id = request.args.get("customer_id")
        assigned_to = request.args.get("assigned_to")
        ticket_id = request.args.get("ticket_id")
        assigned_to = request.args.get("assigned_to")
        query = """
            SELECT id, customer_id, title, priority, status, created_at, updated_at, assigned_to
            FROM tickets
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND status = %s"
            params.append(status)

        if priority:
            query += " AND priority = %s"
            params.append(priority)

        if customer_id:
            query += " AND customer_id = %s"
            params.append(customer_id)
        

        if assigned_to:
          query += " AND assigned_to = %s"
          params.append(assigned_to)

        if ticket_id:
            query += " AND id = %s"
            params.append(ticket_id)

        query += " ORDER BY created_at DESC"

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, tuple(params))

        tickets = cursor.fetchall()
        return jsonify(tickets), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
            conn.close()



from typing import Literal

@tickets_bp.route("/tickets/<int:ticket_id>/update", methods=["PUT"])
def update_ticket_status(ticket_id):
    """
    Update ticket 
    ---
    tags:
      - Tickets
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [OPEN, IN_PROGRESS, CLOSED]
    responses:
      200:
        description: Status updated
      400:
        description: Bad request
      404:
        description: Ticket not found
    """
    try:
        body = request.json
        new_status = body.get("status")
        assigned_to = body.get("assigned_to")

        if new_status not in ["OPEN", "IN_PROGRESS", "CLOSED"]:
            return jsonify({"error": "Invalid status"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check ticket exists
        cursor.execute("SELECT status FROM tickets WHERE id = %s", (ticket_id,))
        ticket = cursor.fetchone()

        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404

        # Optional rule: don't reopen closed ticket
        if ticket["status"] == "CLOSED" and new_status != "CLOSED":
            return jsonify({"error": "Closed tickets cannot be reopened"}), 400

        # Update status
        cursor.execute("""
            UPDATE tickets
            SET status = %s, assigned_to = %s
            WHERE id = %s
        """, (new_status, assigned_to, ticket_id))

        conn.commit()

        # Invalidate dashboard cache
        delete_cached("dashboard:summary")

        return jsonify({"message": "Status updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
            conn.close()

@tickets_bp.route("/tickets/<int:ticket_id>/assign", methods=["PUT"])
def assign_ticket(ticket_id):
    """
    Assign a ticket to a support agent
    ---
    tags:
      - Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            assigned_to:
              type: integer
              example: 3
    responses:
      200:
        description: Ticket assigned
    """
    data = request.json
    assigned_to = data.get("assigned_to")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check ticket exists
    cursor.execute("SELECT id FROM tickets WHERE id=%s", (ticket_id,))
    if not cursor.fetchone():
        return jsonify({"error": "Ticket not found"}), 404

    # Check user is real
    cursor.execute("SELECT id, role FROM users WHERE id=%s", (assigned_to,))
    user = cursor.fetchone()
    if not user or user["role"] != "agent":
        return jsonify({"error": "User must be a valid AGENT"}), 400

    cursor.execute("""
        UPDATE tickets
        SET assigned_to=%s
        WHERE id=%s
    """, (assigned_to, ticket_id))

    conn.commit()
    delete_cached("dashboard:summary")
    
    return jsonify({"message": "Ticket assigned"}), 200

@tickets_bp.route("/tickets/<int:id>", methods=["DELETE"])
def delete_ticket(id):
    """
    Delete a ticket
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tickets WHERE id=%s", (id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Ticket not found"}), 404

        conn.commit()
        return jsonify({"message": "Ticket deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
