# from flask import Blueprint, render_template, request, session
# from control.AutoPublishRulesCTL import AutoPublish
# from control.AdminDashboardCTL import AdminDashboardControl

# auto_publish_bp = Blueprint("auto_publish", __name__)

# @auto_publish_bp.route("/admin/auto-publish-rules", methods=["GET", "POST"])
# def auto_publish_settings_page():
#     admin_control = AdminDashboardControl()
#     admin_data = admin_control.get_dashboard_data()

#     control = AutoPublish()
#     message = ""
#     error = ""

#     if request.method == "POST":
#         min_credibility_score = request.form.get("minCredibilityScore", "").strip()
#         updated_by = session["userID"]

#         success, response_message = control.saveAutoPublishRules(min_credibility_score, updated_by)

#         if success:
#             message = response_message
#         else:
#             error = response_message

#     current_rule = control.getCurrentAutoPublishRule()

#     return render_template(
#         "auto_publish_rules.html",
#         admin=admin_data["admin"],
#         current_rule=current_rule,
#         message=message,
#         error=error
#     )

from flask import Blueprint, render_template, request, session
from control.AutoPublishRulesCTL import AutoPublish
from control.AdminDashboardCTL import AdminDashboardControl

auto_publish_bp = Blueprint("auto_publish", __name__)

@auto_publish_bp.route("/admin/auto-publish-rules", methods=["GET", "POST"])
def auto_publish_settings_page():
    admin_control = AdminDashboardControl()
    admin_data = admin_control.get_dashboard_data()

    control = AutoPublish()
    message = ""
    error = ""

    if request.method == "POST":
        updated_by = session.get("userID")

        auto_success, auto_message = control.saveAutoPublishRules(
            request.form.get("minCredibilityScore", "").strip(),
            updated_by
        )

        credibility_success, credibility_message = control.update_credibility_thresholds(
            request.form,
            updated_by
        )

        if auto_success and credibility_success:
            message = "Configuration saved successfully."
        else:
            errors = []
            if not auto_success:
                errors.append(auto_message)
            if not credibility_success:
                errors.append(credibility_message)
            error = " ".join(errors)

    current_rule = control.getCurrentAutoPublishRule()
    current_credibility_rule = control.getCurrentCredibilityStatusRule()

    return render_template(
        "auto_publish_rules.html",
        admin=admin_data["admin"],
        current_rule=current_rule,
        current_credibility_rule=current_credibility_rule,
        message=message,
        error=error
    )