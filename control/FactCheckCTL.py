import re
import spacy
import os
import requests

nlp = spacy.load("en_core_web_sm")

class FactCheckController:

    @staticmethod
    def split_sentences(text):
        doc = nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    @staticmethod
    def extract_entities(sentence):
        doc = nlp(sentence)
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    @staticmethod
    def has_number(sentence):
        return any(char.isdigit() for char in sentence)

    @staticmethod
    def is_opinion(sentence):
        lower = sentence.lower()
        opinion_phrases = [
            "i think",
            "in my opinion",
            "perhaps",
            "it seems",
            "i believe",
            "maybe"
        ]
        return any(phrase in lower for phrase in opinion_phrases)

    @staticmethod
    def has_strong_claim(sentence):
        lower = sentence.lower()
        strong_words = [
            "worst",
            "best",
            "always",
            "never",
            "completely failed",
            "definitely",
            "undeniably"
        ]
        return any(word in lower for word in strong_words)

    @classmethod
    def classify_sentence(cls, sentence):
        entities = cls.extract_entities(sentence)
        entity_labels = [ent["label"] for ent in entities]
        lower = sentence.lower()
        reporting_phrases = [
            "said", "according to", "reported", "announced",
            "received", "awarded", "came in", "won", "bagged",
            "held in", "issued", "stated"
        ]

        ranking_words = ["first", "second", "third", "fourth", "fifth"]

        if any(phrase in lower for phrase in reporting_phrases):
            return {
                "text": sentence,
                "label": "reported_fact",
                "reason": "This sentence appears to be standard news reporting and is lower risk.",
                "entities": entities
            }

        if any(word in lower for word in ranking_words) and any(label in entity_labels for label in ["ORG", "GPE", "PERSON"]):
            return {
                "text": sentence,
                "label": "reported_fact",
                "reason": "This sentence appears to describe rankings or reported results and is lower risk.",
                "entities": entities
            }

        if cls.is_opinion(sentence):
            return {
                "text": sentence,
                "label": "opinion",
                "reason": "This sentence appears to express an opinion.",
                "entities": entities
            }

        if any(word in lower for word in ["vaccine", "virus", "disease", "covid", "cancer", "treatment", "medicine"]):
            fact_check_result = cls.lookup_google_fact_check(sentence)

            if fact_check_result and fact_check_result.get("matched"):
                rating_text = fact_check_result.get("rating", "").lower()

                if any(word in rating_text for word in [
                    "false",
                    "false claim",
                    "misleading",
                    "no evidence",
                    "incorrect",
                    "unsupported",
                    "disprove",
                    "not true",
                    "no proof"
                ]):
                    return {
                        "text": sentence,
                        "label": "contradicted",
                        "reason": f"External fact-check found from {fact_check_result['publisher']} with rating: {fact_check_result['rating']}.",
                        "entities": entities,
                        "fact_check_match": fact_check_result
                    }

                return {
                    "text": sentence,
                    "label": "needs_evidence",
                    "reason": f"Related reviewed claim found from {fact_check_result['publisher']} with rating: {fact_check_result['rating']}. Manual review recommended.",
                    "entities": entities,
                    "fact_check_match": fact_check_result
                }
            return {
                "text": sentence,
                "label": "needs_evidence",
                "reason": "This sentence contains a health-related claim that requires verification.",
                "entities": entities
            }

        if cls.has_number(sentence) and any(word in lower for word in ["rate", "increase", "decrease", "%", "percent", "million", "billion"]):
            return {
                "text": sentence,
                "label": "needs_evidence",
                "reason": "This sentence contains numbers or statistics that should be verified.",
                "entities": entities
            }

        # Only flag if entity + strong claim
        if any(label in entity_labels for label in ["PERSON", "ORG", "GPE"]) and cls.has_strong_claim(sentence):
            return {
                "text": sentence,
                "label": "needs_evidence",
                "reason": "This sentence makes a strong claim involving entities and should be verified.",
                "entities": entities
            }

        if cls.has_strong_claim(sentence):
            return {
                "text": sentence,
                "label": "needs_evidence",
                "reason": "This sentence contains strong or exaggerated wording and should be checked.",
                "entities": entities
            }

        return {
            "text": sentence,
            "label": "needs_evidence",
            "reason": "This claim requires verification from reliable sources.",
            "entities": entities
        }

    @staticmethod
    def calculate_score(results):
        score = 100

        for item in results:
            text_lower = item["text"].lower()

            if item["label"] == "contradicted":
                score -= 30
                if any(word in text_lower for word in ["vaccine", "virus", "disease", "covid", "cancer"]):
                    score -= 10

            elif item["label"] == "needs_evidence":
                score -= 5

            elif item["label"] == "opinion":
                score -= 2

            elif item["label"] == "reported_fact":
                score -= 0

        return max(0, min(score, 100))

    @staticmethod
    def get_status(score):
        if score >= 80:
            return "High Credibility"
        elif score >= 60:
            return "Moderate Credibility"
        elif score >= 40:
            return "Low Credibility"
        return "High Risk"

    @classmethod
    def analyse_content(cls, content):
        sentences = cls.split_sentences(content)
        results = [cls.classify_sentence(sentence) for sentence in sentences]

        score = cls.calculate_score(results)
        status = cls.get_status(score)

        return {
            "score": score,
            "status": status,
            "sentences": results
        }
    
    @staticmethod
    def lookup_google_fact_check(claim_text):
        api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")

        if not api_key:
            return None

        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            "query": claim_text,
            "key": api_key,
            "languageCode": "en"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            claims = data.get("claims", [])
            if not claims:
                return None

            first_claim = claims[0]
            reviews = first_claim.get("claimReview", [])

            if reviews:
                first_review = reviews[0]
                return {
                    "matched": True,
                    "publisher": first_review.get("publisher", {}).get("name", "Unknown"),
                    "url": first_review.get("url", ""),
                    "rating": first_review.get("textualRating", "No rating")
                }

            return {"matched": True, "publisher": "Unknown", "url": "", "rating": "No rating"}

        except Exception:
            return None