from flask import Blueprint, request, jsonify, session, redirect, current_app
from entity.db_connection import get_db_connection
from datetime import datetime
import math
import os
import uuid
from werkzeug.utils import secure_filename

web_admin_api_bp = Blueprint("web_admin_api", __name__)

# ---------------- COMPANY PROFILE ----------------

@web_admin_api_bp.route("/admin/company-profile", methods=["GET"])
def get_company_profile():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM CompanyProfile ORDER BY profileID ASC LIMIT 1")
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(result if result else {})


@web_admin_api_bp.route("/admin/company-profile", methods=["PUT"])
def update_company_profile():
    data = request.json

    company_name = data.get("companyName")
    description = data.get("description")
    mission = data.get("mission")
    vision = data.get("vision")
    contact_email = data.get("contactEmail")
    contact_phone = data.get("contactPhone")

    updated_by = session.get("userID")

    # ⭐⭐⭐⭐⭐⭐⭐ FIX ⭐⭐⭐⭐⭐⭐⭐
    if not updated_by:
        updated_by = 1   # fallback admin id
    # ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT profileID FROM CompanyProfile ORDER BY profileID ASC LIMIT 1")
    row = cursor.fetchone()

    if row:
        profile_id = row["profileID"]
        cursor.execute("""
            UPDATE CompanyProfile
            SET companyName=%s,
                description=%s,
                mission=%s,
                vision=%s,
                contactEmail=%s,
                contactPhone=%s,
                updated_at=%s,
                updated_by=%s
            WHERE profileID=%s
        """, (
            company_name,
            description,
            mission,
            vision,
            contact_email,
            contact_phone,
            datetime.now(),
            updated_by,
            profile_id
        ))
    else:
        cursor.execute("""
            INSERT INTO CompanyProfile
            (companyName, description, mission, vision, contactEmail, contactPhone, updated_at, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            company_name,
            description,
            mission,
            vision,
            contact_email,
            contact_phone,
            datetime.now(),
            updated_by
        ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Company profile updated successfully"})


# ---------------- SUBSCRIPTION PLAN ----------------

@web_admin_api_bp.route("/admin/subscription-plan", methods=["GET"])
def get_subscription_plan():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM SubscriptionPlan ORDER BY planID ASC LIMIT 1")
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(result if result else {})

@web_admin_api_bp.route("/admin/subscription-plan", methods=["PUT"])
def update_subscription_plan():

    data = request.json

    plan_name = data.get("planName")
    plan_description = data.get("planDescription")
    price = data.get("price")
    billing_cycle = data.get("billingCycle")
    plan_status = data.get("planStatus")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT planID
        FROM SubscriptionPlan
        ORDER BY planID ASC
        LIMIT 1
    """)
    row = cursor.fetchone()

    if row:

        # ⭐⭐⭐⭐⭐ FIX HERE ⭐⭐⭐⭐⭐
        plan_id = row["planID"] if isinstance(row, dict) else row[0]
        # ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐

        cursor.execute("""
            UPDATE SubscriptionPlan
            SET planName=%s,
                planDescription=%s,
                price=%s,
                billingCycle=%s,
                planStatus=%s
            WHERE planID=%s
        """, (
            plan_name,
            plan_description,
            price,
            billing_cycle,
            plan_status,
            plan_id
        ))

    else:

        cursor.execute("""
            INSERT INTO SubscriptionPlan
            (planName, planDescription, price, billingCycle, planStatus)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            plan_name,
            plan_description,
            price,
            billing_cycle,
            plan_status
        ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": "Subscription plan updated successfully"
    })

# -------------------- KEY PRODUCT FEATURES --------------------

UPLOAD_FOLDER = "static/images/webpage"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

class SimplePagination:
    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = math.ceil(total / per_page) if total > 0 else 1

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def next_num(self):
        return self.page + 1

    def iter_pages(self):
        return range(1, self.pages + 1)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_feature_image(image_file):
    if not image_file or image_file.filename == "":
        return None

    if not allowed_file(image_file.filename):
        return None

    filename = secure_filename(image_file.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    new_filename = f"feature_{uuid.uuid4().hex}.{ext}"

    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)

    image_file.save(os.path.join(upload_path, new_filename))
    return new_filename


def delete_feature_image(filename):
    if not filename:
        return

    file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


def get_key_features_paginated(page=1, per_page=3):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM ProductFeature")
    total = cursor.fetchone()["total"]

    offset = (page - 1) * per_page
    cursor.execute("""
        SELECT featureID, featureName, featureImage AS image
        FROM ProductFeature
        ORDER BY featureID ASC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    features = cursor.fetchall()

    cursor.close()
    conn.close()

    pagination = SimplePagination(page, per_page, total)
    return features, pagination


@web_admin_api_bp.route("/admin/key-features/add", methods=["POST"])
def add_key_feature():
    if "userID" not in session:
        return redirect("/login")

    feature_name = request.form.get("featureName", "").strip()
    image_file = request.files.get("image")

    if not feature_name:
        return redirect("/admin/edit-key-product-features")

    if not image_file or image_file.filename == "":
        return "Image is required when adding a new feature.", 400

    image_filename = save_feature_image(image_file)

    if not image_filename:
        return "Invalid image file.", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ProductFeature (featureName, featureImage, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
    """, (
        feature_name,
        image_filename,
        datetime.now(),
        datetime.now()
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/edit-key-product-features")

@web_admin_api_bp.route("/admin/key-features/update", methods=["POST"])
def update_key_feature():
    if "userID" not in session:
        return redirect("/login")

    feature_id = request.form.get("featureID")
    feature_name = request.form.get("featureName", "").strip()
    image_file = request.files.get("image")

    if not feature_id or not feature_name:
        return redirect("/admin/edit-key-product-features")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT featureImage AS image
        FROM ProductFeature
        WHERE featureID = %s
    """, (feature_id,))
    existing = cursor.fetchone()

    if not existing:
        cursor.close()
        conn.close()
        return redirect("/admin/edit-key-product-features")

    image_filename = existing["image"]

    if image_file and image_file.filename != "":
        new_image = save_feature_image(image_file)
        if new_image:
            delete_feature_image(existing["image"])
            image_filename = new_image

    cursor.execute("""
        UPDATE ProductFeature
        SET featureName = %s,
            featureImage = %s,
            updated_at = %s
        WHERE featureID = %s
    """, (
        feature_name,
        image_filename,
        datetime.now(),
        feature_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/edit-key-product-features")


@web_admin_api_bp.route("/admin/key-features/delete/<int:feature_id>", methods=["POST"])
def delete_key_feature(feature_id):
    if "userID" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT featureImage AS image
        FROM ProductFeature
        WHERE featureID = %s
    """, (feature_id,))
    existing = cursor.fetchone()

    if existing:
        delete_feature_image(existing["image"])
        cursor.execute("DELETE FROM ProductFeature WHERE featureID = %s", (feature_id,))
        conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin/edit-key-product-features")

