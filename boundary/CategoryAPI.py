from flask import Blueprint, request, jsonify
import mysql.connector

category_bp = Blueprint("category_api", __name__)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="news_system"
    )


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM ArticleCategory")
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(result)


@category_bp.route("/category", methods=["POST"])
def add_category():
    data = request.json
    name = data.get("categoryName")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO ArticleCategory (categoryName) VALUES (%s)",
        (name,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Category added"})


@category_bp.route("/category/<int:id>", methods=["PUT"])
def update_category(id):
    data = request.json
    name = data.get("categoryName")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE ArticleCategory SET categoryName=%s WHERE categoryID=%s",
        (name, id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Category updated"})


@category_bp.route("/category/<int:id>", methods=["DELETE"])
def delete_category(id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM ArticleCategory WHERE categoryID=%s",
        (id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Category deleted"})
