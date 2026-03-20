from flask import Blueprint, request, jsonify
from control.FactCheckCTL import FactCheckController

fact_check_bp = Blueprint("fact_check", __name__)

@fact_check_bp.route("/fact-check-preview", methods=["POST"])
def fact_check_preview():
    data = request.get_json()
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "No content provided"}), 400

    result = FactCheckController.analyse_content(content)
    return jsonify(result)