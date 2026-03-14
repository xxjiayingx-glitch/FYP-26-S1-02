from flask import Blueprint, request, jsonify, session
import mysql.connector
from datetime import datetime

web_admin_api_bp = Blueprint("web_admin_api", __name__)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="news_system"
    )

# ---------------- COMPANY PROFILE ----------------

@web_admin_api_bp.route("/admin/company-profile", methods=["GET"])
def get_company_profile():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

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

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT profileID FROM CompanyProfile ORDER BY profileID ASC LIMIT 1")
    row = cursor.fetchone()

    if row:
        profile_id = row[0]
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
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

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

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT planID FROM SubscriptionPlan ORDER BY planID ASC LIMIT 1")
    row = cursor.fetchone()

    if row:
        plan_id = row[0]
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

    return jsonify({"message": "Subscription plan updated successfully"})
