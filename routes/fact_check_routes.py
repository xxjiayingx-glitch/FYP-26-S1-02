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

# from flask import Blueprint, request, jsonify
# from control.FactCheckCTL import FactCheckController

# fact_check_bp = Blueprint("fact_check", __name__)

# @fact_check_bp.route("/fact-check-preview", methods=["POST"])
# def fact_check_preview():
#     try:
#         data = request.get_json()

#         if not data:
#             return jsonify({"error": "Invalid JSON body"}), 400

#         content = data.get("content", "").strip()

#         if not content:
#             return jsonify({"error": "No content provided"}), 400

#         # Prevent meaningless checks on very short text
#         if len(content.split()) < 10:
#             return jsonify({"error": "Content too short to fact-check. Please provide at least a sentence or two."}), 400

#         result = FactCheckController.analyse_content(content)
#         return jsonify(result)

#     except Exception as e:
#         print("FACT CHECK ERROR:", e)
#         return jsonify({"error": str(e)}), 500

from flask import Blueprint, request, jsonify
from control.FactCheckCTL import FactCheckController
from entity.Article import Article  # adjust if your entity name is different

fact_check_bp = Blueprint("fact_check", __name__)

@fact_check_bp.route("/fact-check-preview", methods=["POST"])
def fact_check_preview():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        title = data.get("title", "").strip()
        content = data.get("content", "").strip()
        category_id = data.get("category")

        if not content:
            return jsonify({"error": "No content provided"}), 400

        if len(content.split()) < 10:
            return jsonify({"error": "Content too short to fact-check. Please provide at least a sentence or two."}), 400

        selected_category = None
        available_categories = []

        category_entity = Article()
        categories = category_entity.get_categories()  # change to your actual method name

        for cat in categories:
            available_categories.append(cat["categoryName"])

            if str(cat["categoryID"]) == str(category_id):
                selected_category = cat["categoryName"]

        result = FactCheckController.analyse_content(
            content,
            title=title,
            selected_category=selected_category,
            available_categories=available_categories
        )

        return jsonify(result)

    except Exception as e:
        print("FACT CHECK ERROR:", e)
        return jsonify({"error": str(e)}), 500