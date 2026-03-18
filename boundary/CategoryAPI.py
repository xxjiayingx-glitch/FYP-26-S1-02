from flask import Blueprint, request, jsonify
from entity.db_connection import get_db_connection

category_bp = Blueprint("category_api", __name__)



@category_bp.route("/admin/categories", methods=["GET"])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ArticleCategory")
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(result)


@category_bp.route("/admin/category", methods=["POST"])
def add_category():
    data = request.json
    name = data.get("categoryName")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO ArticleCategory (categoryName) VALUES (%s)",
        (name,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Category added"})


@category_bp.route("/admin/category/<int:id>", methods=["PUT"])
def update_category(id):
    data = request.json
    name = data.get("categoryName")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE ArticleCategory SET categoryName=%s WHERE categoryID=%s",
        (name, id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Category updated"})


@category_bp.route("/admin/category/<int:id>", methods=["DELETE"])
def delete_category(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM ArticleCategory WHERE categoryID=%s",
        (id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Category deleted"})
