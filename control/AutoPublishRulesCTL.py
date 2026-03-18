from entity.AutoPublishRule import AutoPublishRule

class AutoPublish:
    def saveAutoPublishRules(self, minCredibilityScore, updated_by):
        # validation
        if minCredibilityScore == "":
            return False, "Invalid credibility score threshold."

        try:
            score = float(minCredibilityScore)
        except ValueError:
            return False, "Invalid credibility score threshold."

        # Assume 0 - 100 scale
        if score < 0 or score > 100:
            return False, "Invalid credibility score threshold."

        success = AutoPublishRule.updateAutoPublishRules(score, updated_by)

        if success:
            return True, "Configuration saved successfully."
        return False, "Failed to save configuration."

    def getCurrentAutoPublishRule(self):
        return AutoPublishRule.getCurrentRule()