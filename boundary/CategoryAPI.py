from flask import Blueprint, request, jsonify, session
from entity.db_connection import get_db_connection
import pymysql.cursors

category_bp = Blueprint("category_api", __name__)


# ⭐ GET ALL
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


# ⭐ ADD
@category_bp.route("/admin/category", methods=["POST"])
def add_category():

    data = request.get_json()
    name = data.get("categoryName")

    if not name:
        return jsonify({"message": "Category name missing"}), 400

    created_by = session.get("userID")   # ⭐⭐⭐ 改这里！！！

    if not created_by:
        return jsonify({"message": "Session expired"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO ArticleCategory
        (categoryName, categoryStatus, created_by)
        VALUES (%s, %s, %s)
        """,
        (name, "active", created_by)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Category added successfully"})

# ⭐ UPDATE
@category_bp.route("/admin/category/<int:id>", methods=["PUT"])
def update_category(id):
    try:
        data = request.get_json()
        name = data.get("categoryName")

        if not name:
            return jsonify({"message": "Category name missing"}), 400

        updated_by = session.get("adminID")

        conn = get_db_connection()
        cursor = conn.cursor()

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


# ⭐ DELETE
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
