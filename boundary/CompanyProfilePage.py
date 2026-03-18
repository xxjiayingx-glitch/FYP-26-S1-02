from flask import Blueprint, render_template
from control.UnregisteredUser.ViewCompanyProfileCTL import CompanyProfileController

companyprof_bp = Blueprint('companyprofile', __name__)
companyprofileCTL = CompanyProfileController()

@companyprof_bp.route("/companyprofile")
def unreg_companyprof():
    profile = companyprofileCTL.getCompanyProfile()

    return render_template(
        "Unregistered/UnregCompanyProf.html",
        profile=profile
    )
