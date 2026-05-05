# from entity.AutoPublishRule import AutoPublishRule
# from entity.CredibilityStatusRule import CredibilityStatusRule

# class AutoPublish:
#     def saveAutoPublishRules(self, minCredibilityScore, updated_by):
#         # validation
#         if minCredibilityScore == "":
#             return False, "Invalid credibility score threshold."

#         try:
#             score = float(minCredibilityScore)
#         except ValueError:
#             return False, "Invalid credibility score threshold."

#         # Assume 0 - 100 scale
#         if score < 0 or score > 100:
#             return False, "Invalid credibility score threshold."

#         success = AutoPublishRule.updateAutoPublishRules(score, updated_by)

#         if success:
#             return True, "Configuration saved successfully."
#         return False, "Failed to save configuration."

#     def getCurrentAutoPublishRule(self):
#         return AutoPublishRule.getCurrentRule()
    
    
#     #-----------------------------------#
#     # update credibility threholds rule #
#     #-----------------------------------#
#     def getCurrentCredibilityStatusRule(self):
#         return CredibilityStatusRule.get_active_rule()

#     def update_credibility_thresholds(self, form_data, admin_id):
#         try:
#             verified = float(form_data.get("verifiedMinScore", 0))
#             highly_credible = float(form_data.get("highlyCredibleMinScore", 0))
#             generally_reliable = float(form_data.get("generallyReliableMinScore", 0))
#             mixed = float(form_data.get("mixedMinScore", 0))
#             low_confidence = float(form_data.get("lowConfidenceMinScore", 0))
#             misleading_cutoff = float(form_data.get("misleadingCutoffScore", 0))
#         except ValueError:
#             return False, "All threshold values must be numeric."

#         values = [
#             verified,
#             highly_credible,
#             generally_reliable,
#             mixed,
#             low_confidence,
#             misleading_cutoff
#         ]

#         if any(v < 0 or v > 100 for v in values):
#             return False, "All threshold values must be between 0 and 100."

#         if not (verified >= highly_credible >= generally_reliable >= mixed >= low_confidence):
#             return False, "Threshold order must be: Verified ≥ Highly Credible ≥ Generally Reliable ≥ Mixed ≥ Low Confidence."

#         updated = CredibilityStatusRule.update_active_rule(
#             verified,
#             highly_credible,
#             generally_reliable,
#             mixed,
#             low_confidence,
#             misleading_cutoff,
#             admin_id
#         )

#         if not updated:
#             return False, "Failed to update credibility thresholds."

#         return True, "Credibility thresholds updated successfully."
    

from entity.AutoPublishRule import AutoPublishRule
from entity.CredibilityStatusRule import CredibilityStatusRule

class AutoPublish:
    def saveAutoPublishRules(self, minCredibilityScore, updated_by):
        if minCredibilityScore == "":
            return False, "Invalid credibility score threshold."

        try:
            score = float(minCredibilityScore)
        except ValueError:
            return False, "Invalid credibility score threshold."

        if score < 0 or score > 100:
            return False, "Invalid credibility score threshold."

        success = AutoPublishRule.updateAutoPublishRules(score, updated_by)

        if success:
            return True, "Configuration saved successfully."
        return False, "Failed to save configuration."

    def getCurrentAutoPublishRule(self):
        return AutoPublishRule.getCurrentRule()

    def getCurrentCredibilityStatusRule(self):
        return CredibilityStatusRule.get_active_rule()
    
    #-----------------------------------#
    # update credibility threholds rule #
    #-----------------------------------#

    def update_credibility_thresholds(self, form_data, admin_id):
        try:
            verified = float(form_data.get("verifiedMinScore", 0))
            highly_credible = float(form_data.get("highlyCredibleMinScore", 0))
            generally_reliable = float(form_data.get("generallyReliableMinScore", 0))
            mixed = float(form_data.get("mixedMinScore", 0))
            low_confidence = float(form_data.get("lowConfidenceMinScore", 0))
        except ValueError:
            return False, "All threshold values must be numeric."

        values = [
            verified,
            highly_credible,
            generally_reliable,
            mixed,
            low_confidence
        ]

        if any(v < 0 or v > 100 for v in values):
            return False, "All threshold values must be between 0 and 100."

        if not (verified >= highly_credible >= generally_reliable >= mixed >= low_confidence):
            return False, "Threshold order must be: Verified ≥ Highly Credible ≥ Generally Reliable ≥ Mixed ≥ Low Confidence."

        updated = CredibilityStatusRule.update_active_rule(
            verified,
            highly_credible,
            generally_reliable,
            mixed,
            low_confidence,
            admin_id
        )

        if not updated:
            return False, "Failed to update credibility thresholds."

        return True, "Credibility thresholds updated successfully."