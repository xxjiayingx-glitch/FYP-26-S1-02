from flask import Blueprint, request, jsonify, session
from entity.db_connection import get_db_connection
import pymysql.cursors

category_bp = Blueprint("category_api", __name__)

def category_exists(cursor, name, exclude_id=None):
    if exclude_id:
        cursor.execute(
            """
            SELECT categoryID
            FROM ArticleCategory
            WHERE LOWER(TRIM(categoryName)) = LOWER(TRIM(%s))
            AND categoryID != %s
            """,
            (name, exclude_id)
        )
    else:
        cursor.execute(
            """
            SELECT categoryID
            FROM ArticleCategory
            WHERE LOWER(TRIM(categoryName)) = LOWER(TRIM(%s))
            """,
            (name,)
        )

    return cursor.fetchone() is not None

# GET ALL
@category_bp.route("/admin/categories", methods=["GET"])
def get_categories():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT * FROM ArticleCategory ORDER BY categoryID DESC")
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(result)

    except Exception as e:
        print("GET CATEGORY ERROR:", e)
        return jsonify({"message": "Server error"}), 500


# ADD
@category_bp.route("/admin/category", methods=["POST"])
def add_category():
    conn = None
    cursor = None

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"message": "Invalid request data"}), 400

        name = data.get("categoryName")

        if not name or not name.strip():
            return jsonify({"message": "Category name missing"}), 400

        name = name.strip()

        created_by = session.get("userID")

        if not created_by:
            return jsonify({"message": "Session expired. Please login again."}), 401

        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Check duplicate category
        cursor.execute(
            """
            SELECT categoryID
            FROM ArticleCategory
            WHERE LOWER(TRIM(categoryName)) = LOWER(TRIM(%s))
            LIMIT 1
            """,
            (name,)
        )

        existing_category = cursor.fetchone()

        if existing_category:
            return jsonify({"message": "Category already exists"}), 409

        cursor.execute(
            """
            INSERT INTO ArticleCategory
            (categoryName, categoryStatus, created_by)
            VALUES (%s, %s, %s)
            """,
            (name, "active", created_by)
        )

        conn.commit()

        return jsonify({"message": "Category added successfully"}), 201

    except Exception as e:
        if conn:
            conn.rollback()

        print("ADD CATEGORY ERROR:", e)
        return jsonify({"message": "Server error while adding category"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# UPDATE
@category_bp.route("/admin/category/<int:id>", methods=["PUT"])
def update_category(id):
    try:
        data = request.get_json()
        name = data.get("categoryName", "").strip()

        if not name:
            return jsonify({"message": "Category name missing"}), 400

        updated_by = session.get("userID")

        if not updated_by:
            return jsonify({"message": "Session expired"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check duplicate category, excluding current category ID
        if category_exists(cursor, name, exclude_id=id):
            cursor.close()
            conn.close()
            return jsonify({"message": "Category already exists"}), 409

        cursor.execute(
            """
            UPDATE ArticleCategory
            SET categoryName=%s,
                updated_by=%s
            WHERE categoryID=%s
            """,
            (name, updated_by, id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Category updated successfully"})

    except Exception as e:
        print("UPDATE CATEGORY ERROR:", e)
        return jsonify({"message": "Server error"}), 500


# DELETE
@category_bp.route("/admin/category/<int:id>", methods=["DELETE"])
def delete_category(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM ArticleCategory WHERE categoryID=%s",
            (id,)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Category deleted successfully"})

    except Exception as e:
        print("DELETE CATEGORY ERROR:", e)
        return jsonify({"message": "Server error"}), 500
