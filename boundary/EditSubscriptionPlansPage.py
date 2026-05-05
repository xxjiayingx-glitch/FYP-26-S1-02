# from flask import Blueprint, render_template, session, redirect, url_for, request
# from entity.db_connection import get_db_connection

# edit_subscription_plans_bp = Blueprint(
#     "edit_subscription_plans_bp",
#     __name__
# )

# @edit_subscription_plans_bp.route("/admin/edit-subscription-plans")
# def edit_subscription_plans_page():

#     if "userID" not in session:
#         return redirect(url_for("login.login"))

#     admin = {
#         "userID": session.get("userID"),
#         "username": session.get("username"),
#         "userType": session.get("userType"),
#         "profileImage": session.get("profileImage")
#     }

#     data = request.get_json()

#     plan_name = data.get("planName", "").strip()
#     plan_description = data.get("planDescription", "").strip()
#     price = data.get("price")
#     billing_cycle = data.get("billingCycle", "").strip()
#     plan_status = data.get("planStatus", "").strip().lower()

#     selected_plan_id = request.args.get("planID", type=int)

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT planID, planName
#         FROM SubscriptionPlan
#         ORDER BY planID ASC
#     """)
#     plans = cursor.fetchall()

#     # if no planID is provided, default to first available plan
#     if selected_plan_id is None and plans:
#         selected_plan_id = plans[0]["planID"]
    
#     plan = None
#     if selected_plan_id is not None:
#         cursor.execute("""
#             SELECT *
#             FROM SubscriptionPlan
#             WHERE planID = %s
#             LIMIT 1
#         """, (selected_plan_id,))
#         plan = cursor.fetchone()

#     cursor.close()
#     conn.close()

#     return render_template(
#         "EditSubscriptionPlans.html",
#         admin=admin,
#         plan=plan,
#         plans=plans
#         selected_plan_id=selected_plan_id
#     )

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from entity.db_connection import get_db_connection

edit_subscription_plans_bp = Blueprint(
    "edit_subscription_plans_bp",
    __name__
)


@edit_subscription_plans_bp.route("/admin/edit-subscription-plans")
def edit_subscription_plans_page():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin = {
        "userID": session.get("userID"),
        "username": session.get("username"),
        "userType": session.get("userType"),
        "profileImage": session.get("profileImage")
    }

    selected_plan_id = request.args.get("planID", type=int)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all plans for dropdown
    cursor.execute("""
        SELECT planID, planName
        FROM SubscriptionPlan
        ORDER BY planID ASC
    """)
    plans = cursor.fetchall()

    # Default to first plan if no planID is provided
    if selected_plan_id is None and plans:
        selected_plan_id = plans[0]["planID"]

    plan = None
    if selected_plan_id is not None:
        cursor.execute("""
            SELECT *
            FROM SubscriptionPlan
            WHERE planID = %s
            LIMIT 1
        """, (selected_plan_id,))
        plan = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "EditSubscriptionPlans.html",
        admin=admin,
        plan=plan,
        plans=plans,
        selected_plan_id=selected_plan_id
    )


@edit_subscription_plans_bp.route("/admin/subscription-plan", methods=["POST", "PUT"])
def manage_subscription_plan():
    if "userID" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401
    
    current_user_id = session.get("userID")

    data = request.get_json()

    plan_id = data.get("planID")
    plan_name = data.get("planName", "").strip()
    plan_description = data.get("planDescription", "").strip()
    plan_features = data.get("planFeatures", "").strip()
    price = data.get("price")
    billing_cycle = data.get("billingCycle", "").strip()
    plan_status = data.get("planStatus", "").strip().lower()

    # Basic validation
    if not plan_name or not plan_description or not plan_features or price in (None, "") or not billing_cycle or not plan_status:
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    try:
        price = float(price)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid price value"
        }), 400

    if price < 0:
        return jsonify({
            "success": False,
            "message": "Price cannot be negative"
        }), 400

    if plan_status not in ["active", "inactive"]:
        return jsonify({
            "success": False,
            "message": "Invalid plan status"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # POST = Create new plan
        if request.method == "POST":
            cursor.execute("""
                SELECT planID
                FROM SubscriptionPlan
                WHERE LOWER(TRIM(planName)) = LOWER(TRIM(%s))
                LIMIT 1
            """, (plan_name,))
            existing_plan = cursor.fetchone()

            if existing_plan:
                return jsonify({
                    "success": False,
                    "message": "A subscription plan with the same name already exists"
                }), 409

            cursor.execute("""
                INSERT INTO SubscriptionPlan (
                    planName,
                    planDescription,
                    planFeatures,
                    price,
                    billingCycle,
                    planStatus,
                    created_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                plan_name,
                plan_description,
                plan_features,
                price,
                billing_cycle,
                plan_status,
                current_user_id
            ))

            conn.commit()

            return jsonify({
                "success": True,
                "message": "Subscription plan created successfully"
            }), 201

        # PUT = Update existing plan
        if request.method == "PUT":
            if plan_id is None:
                return jsonify({
                    "success": False,
                    "message": "planID is required for update"
                }), 400

            # Check whether the plan really exists first
            cursor.execute("""
                SELECT planID
                FROM SubscriptionPlan
                WHERE planID = %s
                LIMIT 1
            """, (plan_id,))
            existing_plan = cursor.fetchone()

            if not existing_plan:
                return jsonify({
                    "success": False,
                    "message": "Subscription plan not found"
                }), 404

            # Check duplicate plan name, excluding current plan
            cursor.execute("""
                SELECT planID
                FROM SubscriptionPlan
                WHERE LOWER(TRIM(planName)) = LOWER(TRIM(%s))
                  AND planID != %s
                LIMIT 1
            """, (plan_name, plan_id))
            duplicate_plan = cursor.fetchone()

            if duplicate_plan:
                return jsonify({
                    "success": False,
                    "message": "Another subscription plan with the same name already exists"
                }), 409

            cursor.execute("""
                UPDATE SubscriptionPlan
                SET
                    planName = %s,
                    planDescription = %s,
                    planFeatures = %s,
                    price = %s,
                    billingCycle = %s,
                    planStatus = %s,
                    updated_by = %s
                WHERE planID = %s
            """, (
                plan_name,
                plan_description,
                plan_features,
                price,
                billing_cycle,
                plan_status,
                current_user_id,
                plan_id
            ))

            conn.commit()

            return jsonify({
                "success": True,
                "message": "Subscription plan updated successfully"
            }), 200

    except Exception as e:
        conn.rollback()
        print("Subscription plan error:", e)
        return jsonify({
            "success": False,
            "message": "Unable to save subscription plan"
        }), 500

    finally:
        cursor.close()
        conn.close()