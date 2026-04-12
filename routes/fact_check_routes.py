# from flask import Blueprint, request, jsonify
# from control.FactCheckCTL import FactCheckController

# fact_check_bp = Blueprint("fact_check", __name__)

# @fact_check_bp.route("/fact-check-preview", methods=["POST"])
# def fact_check_preview():
#     try:
#         data = request.get_json()
#         content = data.get("content", "").strip()

#         if not content:
#             return jsonify({"error": "No content provided"}), 400

#         result = FactCheckController.analyse_content(content)
#         return jsonify(result)
        
#     except Exception as e:
#         print("FACT CHECK ERROR:", e)
#         return jsonify({"error": str(e)}), 500

from flask import Blueprint, request, jsonify
from control.FactCheckCTL import FactCheckController

fact_check_bp = Blueprint("fact_check", __name__)

@fact_check_bp.route("/fact-check-preview", methods=["POST"])
def fact_check_preview():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        content = data.get("content", "").strip()

        if not content:
            return jsonify({"error": "No content provided"}), 400

        # Prevent meaningless checks on very short text
        if len(content.split()) < 10:
            return jsonify({"error": "Content too short to fact-check. Please provide at least a sentence or two."}), 400

        result = FactCheckController.analyse_content(content)
        return jsonify(result)

    except Exception as e:
        print("FACT CHECK ERROR:", e)
        return jsonify({"error": str(e)}), 500