from flask import Blueprint, render_template, session, redirect, url_for, flash,request
from control.VerifiedBadgeAdminCTL import VerifiedBadgeAdminCTL
from control.AdminDashboardCTL import AdminDashboardControl
from control.UpdateProfileCTL import UpdateProfileCTL
import math

admin_verified_bp = Blueprint("admin_verified", __name__)

@admin_verified_bp.route("/admin/verified-badge-mgmt")
def verified_badge_mgmt_pg():
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if session.get("userType") != "system admin":
        return redirect("login.login")
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()
    
    return render_template("admin_verified_badge_mgmt.html", admin=admin_data["admin"])

# View Page
@admin_verified_bp.route("/admin/verified-requests")
def view_verified_requests():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    if session.get("userType") != "system admin":
        return redirect(url_for("login.login"))
    
    page = request.args.get("page", 1, type=int)
    per_page = 20
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()

    try:
        requests = VerifiedBadgeAdminCTL.get_pending_requests()
        print("REQUESTS:", requests)
    except Exception as e:
        print("ERROR:", e) 
        flash(str(e))

    total_requests = len(requests)
    total_pages = math.ceil(total_requests/per_page) if total_requests > 0 else 1

    start = (page-1) * per_page
    end = start + per_page
    pendingRequests = requests[start:end]

    print("TOTAL:", len(requests))
    print("START:", start, "END:", end)
    print("SLICE:", requests[start:end])

    return render_template("admin_verify_badge.html", pendingRequests=pendingRequests, admin=admin_data["admin"], page=page, total_pages=total_pages)

# Approve
@admin_verified_bp.route("/admin/verified-approve/<int:userID>", methods=["POST"])
def approve_verified(userID):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    if session.get("userType") != "system admin":
        return redirect(url_for("login.login"))

    try:
        VerifiedBadgeAdminCTL.approve(userID)
        flash("User verified successfully.")
    except ValueError as e:
        flash(str(e))

    return redirect(url_for("admin_verified.view_verified_requests"))

# Reject
@admin_verified_bp.route("/admin/verified-reject/<int:userID>", methods=["POST"])
def reject_verified(userID):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    if session.get("userType") != "system admin":
        return redirect(url_for("login.login"))

    try:
        VerifiedBadgeAdminCTL.reject(userID)
        flash("Verification rejected.")
    except ValueError as e:
        flash(str(e))

    return redirect(url_for("admin_verified.view_verified_requests"))

@admin_verified_bp.route("/admin/verified-badge-rule", methods=["GET"])
def verified_badge_rule_page():
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if session.get("userType") != "system admin":
        return redirect("login.login")
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()

    eligibility_rule = UpdateProfileCTL.get_verified_badge_rule()

    return render_template(
        "admin_verified_badge_rule.html",
        eligibility_rule=eligibility_rule,
        admin=admin_data["admin"]
    )

@admin_verified_bp.route("/admin/verified-badge-rule/update", methods=["POST"])
def update_verified_badge_rule():
    required_article_count = int(request.form.get("required_article_count", 0))
    minimum_factcheck_score = float(request.form.get("minimum_factcheck_score", 0))
    admin_id = session.get("userID")

    result = VerifiedBadgeAdminCTL.update_verified_badge_rule(
        required_article_count,
        minimum_factcheck_score,
        admin_id
    )

    if result:
        flash("Verified badge rule updated successfully.", "success")
    else:
        flash("Failed to update verified badge rule.", "error")

    return redirect(url_for("admin_verified.verified_badge_rule_page"))
