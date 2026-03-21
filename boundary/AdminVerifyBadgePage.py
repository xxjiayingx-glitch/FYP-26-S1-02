from flask import Blueprint, render_template, session, redirect, url_for, flash
from control.VerifiedBadgeAdminCTL import VerifiedBadgeAdminCTL
from control.AdminDashboardCTL import AdminDashboardControl

admin_verified_bp = Blueprint("admin_verified", __name__)

# View Page
@admin_verified_bp.route("/admin/verified-requests")
def view_verified_requests():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    if session.get("userType") != "system admin":
        return redirect(url_for("login.login"))
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()

    try:
        requests = VerifiedBadgeAdminCTL.get_pending_requests()
    except Exception as e:
        flash(str(e))
        requests = []

    return render_template("admin_verify_badge.html", requests=requests, admin=admin_data["admin"])

# Approve
@admin_verified_bp.route("/admin/verified-approve/<int:userID>", methods=["POST"])
def approve_verified(userID):
    try:
        VerifiedBadgeAdminCTL.approve(userID)
        flash("User verified successfully.")
    except ValueError as e:
        flash(str(e))

    return redirect(url_for("admin_verified.view_verified_requests"))

# Reject
@admin_verified_bp.route("/admin/verified-reject/<int:userID>", methods=["POST"])
def reject_verified(userID):
    try:
        VerifiedBadgeAdminCTL.reject(userID)
        flash("Verification rejected.")
    except ValueError as e:
        flash(str(e))

    return redirect(url_for("admin_verified.view_verified_requests"))