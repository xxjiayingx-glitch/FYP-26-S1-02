from flask import Blueprint, render_template

companyprof_bp = Blueprint('companyprofile', __name__)

@companyprof_bp.route("/companyprofile")
def unreg_companyprof():
    return render_template("Unregistered/UnregCompanyProf.html")