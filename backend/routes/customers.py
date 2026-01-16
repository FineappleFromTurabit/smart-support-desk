# routes/customers.py
from flask import Blueprint, request, jsonify
from schemas.customer import CustomerCreate, CustomerResponse
from db import get_db_connection
from pydantic import ValidationError

customers_bp = Blueprint("customers", __name__)

@customers_bp.route("/customers", methods=["POST"])

def create_customer():
    """
    Create a new customer
    ---
    tags:
      - Customers
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
          properties:
            name:
              type: string
              example: Smit Panchal
            email:
              type: string
              example: smit@gmail.com
            company:
              type: string
              example: Acme Corp
    responses:
      201:
        description: Customer created successfully
      400:
        description: Validation error
      500:
        description: Internal server error
"""
    try:
        data = CustomerCreate(**request.json)

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO customers (name, email, company)
        VALUES (%s, %s, %s)
        """
 
        cursor.execute(query, (data.name, data.email, data.company))
        conn.commit()

        return jsonify({"message": "Customer created"}), 201

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
            conn.close()

@customers_bp.route("/customers", methods=["GET"])
def get_customers():
    """
    Get all customers
    --- 
    tags:
        - Customers
    responses:
      200:
        description: List of customers
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: Smit Panchal
              email:
                type: string
                example: smit@gmail.com
              company:
                type: string
                example: Acme Corp
              created_at:
                type: string
                format: date-time
      500:
        description: Internal server error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id, name, email, company, created_at
            FROM customers
            
        """
        params = []
        if 'customer_name' in request.args:
            query += "where name LIKE %s"
            params.append('%' + request.args['customer_name'] + '%')
        query += " ORDER BY created_at DESC"

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        # Validate output
        customers = [CustomerResponse(**row).dict() for row in rows]

        return jsonify(customers), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
            conn.close()


@customers_bp.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    """
    Delete a customer
    ---
    tags:
      - Customers
    parameters:
      - name: id
        in: path
        required: true
        type: integer
        description: Customer ID
    responses:
      200:
        description: Customer deleted
      404:
        description: Customer not found
      500:
        description: Internal server error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete customer (tickets auto-delete if FK ON DELETE CASCADE)
        query = "DELETE FROM customers WHERE id=%s"
        cursor.execute(query, (id,))

        if cursor.rowcount == 0:
            return jsonify({"error": "Customer not found"}), 404

        conn.commit()
        return jsonify({"message": "Customer deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
            conn.close()
