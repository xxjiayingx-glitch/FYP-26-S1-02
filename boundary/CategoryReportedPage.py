from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from entity.db_connection import get_db_connection

category_reported_page_bp = Blueprint("category_reported_page_bp", __name__)

def report_category_exists(cursor, name, exclude_id=None):
    if exclude_id:
        cursor.execute("""
            SELECT reportCategoryID
            FROM ReportCategory
            WHERE LOWER(TRIM(categoryName)) = LOWER(TRIM(%s))
            AND reportCategoryID != %s
            LIMIT 1
        """, (name, exclude_id))
    else:
        cursor.execute("""
            SELECT reportCategoryID
            FROM ReportCategory
            WHERE LOWER(TRIM(categoryName)) = LOWER(TRIM(%s))
            LIMIT 1
        """, (name,))

    return cursor.fetchone() is not None


@category_reported_page_bp.route("/admin/report-category", methods=["GET", "POST"])
def report_category_page():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin = {
        "userID": session.get("userID"),
        "username": session.get("username"),
        "userType": session.get("userType"),
        "profileImage": session.get("profileImage")
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        category_name = request.form.get("categoryName", "").strip()
        category_status = request.form.get("categoryStatus", "active").strip().lower()
        created_by = session.get("userID")

        if not category_name:
            flash("Category name is required.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for("category_reported_page_bp.report_category_page"))

        # if category_status not in ["active", "inactive"]:
        #     category_status = "active"

        # cursor.execute("""
        #     INSERT INTO ReportCategory (categoryName, categoryStatus, created_by, updated_by)
        #     VALUES (%s, %s, %s, %s)
        # """, (category_name, category_status, created_by, created_by))

        if category_status not in ["active", "inactive"]:
            category_status = "active"

        # Check duplicate report category
        if report_category_exists(cursor, category_name):
            flash("Report category already exists.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for("category_reported_page_bp.report_category_page"))

        cursor.execute("""
            INSERT INTO ReportCategory (categoryName, categoryStatus, created_by, updated_by)
            VALUES (%s, %s, %s, %s)
        """, (category_name, category_status, created_by, created_by))

        conn.commit()
        flash("Report category added successfully.", "success")

        cursor.close()
        conn.close()
        return redirect(url_for("category_reported_page_bp.report_category_page"))

    cursor.execute("""
        SELECT
            reportCategoryID,
            categoryName,
            categoryStatus
        FROM ReportCategory
        ORDER BY reportCategoryID DESC
    """)
    categories = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "category_reported.html",
        admin=admin,
        categories=categories
    )


@category_reported_page_bp.route("/admin/report-category/edit/<int:category_id>", methods=["POST"])
def edit_report_category(category_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    category_name = request.form.get("categoryName", "").strip()
    category_status = request.form.get("categoryStatus", "active").strip().lower()
    updated_by = session.get("userID")

    if not category_name:
        flash("Category name is required.", "error")
        return redirect(url_for("category_reported_page_bp.report_category_page"))

    if category_status not in ["active", "inactive"]:
        category_status = "active"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reportCategoryID
        FROM ReportCategory
        WHERE reportCategoryID = %s
    """, (category_id,))
    category = cursor.fetchone()

    # if not category:
    #     cursor.close()
    #     conn.close()
    #     flash("Report category not found.", "error")
    #     return redirect(url_for("category_reported_page_bp.report_category_page"))

    # cursor.execute("""
    #     UPDATE ReportCategory
    #     SET categoryName = %s,
    #         categoryStatus = %s,
    #         updated_by = %s,
    #         updated_at = CURRENT_TIMESTAMP
    #     WHERE reportCategoryID = %s
    # """, (category_name, category_status, updated_by, category_id))

    if not category:
        cursor.close()
        conn.close()
        flash("Report category not found.", "error")
        return redirect(url_for("category_reported_page_bp.report_category_page"))

    # Check duplicate report category, excluding current category
    if report_category_exists(cursor, category_name, exclude_id=category_id):
        cursor.close()
        conn.close()
        flash("Report category already exists.", "error")
        return redirect(url_for("category_reported_page_bp.report_category_page"))

    cursor.execute("""
        UPDATE ReportCategory
        SET categoryName = %s,
            categoryStatus = %s,
            updated_by = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE reportCategoryID = %s
    """, (category_name, category_status, updated_by, category_id))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Report category updated successfully.", "success")
    return redirect(url_for("category_reported_page_bp.report_category_page"))


@category_reported_page_bp.route("/admin/report-category/delete/<int:category_id>", methods=["POST"])
def delete_report_category(category_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reportCategoryID
        FROM ReportCategory
        WHERE reportCategoryID = %s
    """, (category_id,))
    category = cursor.fetchone()

    if not category:
        cursor.close()
        conn.close()
        flash("Report category not found.", "error")
        return redirect(url_for("category_reported_page_bp.report_category_page"))

    cursor.execute("""
        DELETE FROM ReportCategory
        WHERE reportCategoryID = %s
    """, (category_id,))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Report category deleted successfully.", "success")
    return redirect(url_for("category_reported_page_bp.report_category_page"))
