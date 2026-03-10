from flask import jsonify, request
from flask_cors import cross_origin
from app.entities.CompanyProfile import CompanyProfile
from app.db import get_database
from app.routes.UnregisteredUser_routes import UnregisteredUser


class ViewCompanyProfileCTL:
    def __init__(self):
        self.companyProfile_entity = CompanyProfile()

    def viewCompanyProfile(self, companyID):
        companyProfileList = self.companyProfile_entity.viewCompanyProfile(companyID)
        return companyProfileList


@UnregisteredUser.route("/api/company-profile", methods=["GET"])
def viewCompanyProfile():
    companyID = int(request.args.get("companyID"))
    viewCompanyProfileCTL = ViewCompanyProfileCTL()
    try:
        companyProfileList = viewCompanyProfileCTL.viewCompanyProfile(companyID)

        if companyProfileList:
            return jsonify(companyProfileList), 200
        else:
            return (
                jsonify({
                    "status": "error",
                    "message": "No company profile found"
                }),
                404,
            )

    except Exception as e:
        return (
            jsonify({
                "status": "error",
                "message": str(e),
            }),
            500,
        )