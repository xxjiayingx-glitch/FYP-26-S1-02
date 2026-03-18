from flask import Blueprint, render_template, request
from control.ViewUsersCTL import ViewUsersCTL
from control.SearchUserCTL import SearchUsersCTL
from control.AdminDashboardCTL import AdminDashboardControl
import math

view_users_bp = Blueprint("view_users", __name__)

@view_users_bp.route("/admin/user-accounts", methods=["GET"])
def view_users_page():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    q = request.args.get("q", "").strip()
    user_type = request.args.get("userType", "").strip()
    account_status = request.args.get("accountStatus", "").strip()

    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()

    # If search/filter exists, use SearchUsersCTL
    if q or user_type or account_status:
        search_control = SearchUsersCTL()
        all_users = search_control.searchFilterUsers(q, user_type, account_status)
    else:
        view_control = ViewUsersCTL()
        all_users = view_control.listUsers()

    total_users = len(all_users)
    total_pages = math.ceil(total_users / per_page) if total_users > 0 else 1

    start = (page - 1) * per_page
    end = start + per_page
    users = all_users[start:end]

    return render_template(
        "user_accounts.html",
        admin=admin_data["admin"],
        users=users,
        page=page,
        total_pages=total_pages,
        q=q,
        user_type=user_type,
        account_status=account_status
    )