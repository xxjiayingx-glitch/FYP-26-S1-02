import re
import json
import spacy
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from entity.TrustedStatistics import TrustedStatistic
from entity.LLMCache import LLMCache
# from entity.NewsCache import NewsCache
from entity.FactcheckCache import FactcheckCache
from entity.ClaimVerificationLog import ClaimVerificationLog
from entity.AIFeedbackCache import AIFeedbackCache
from entity.CredibilityStatusRule import CredibilityStatusRule
import time
from datetime import datetime
import logging

AI_CACHE_VERSION = "v2"
AI_CACHE_TTL_DAYS = 30

nlp = spacy.load("en_core_web_sm")

logger = logging.getLogger("factcheck_llm")

if not logger.handlers:
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_llm(model: str, message: str, level: str = "info", **fields) -> None:
    extra = ""
    if fields:
        extra = " | " + " | ".join(f"{k}={v}" for k, v in fields.items())

    final_message = f"[LLM:{model}] {message}{extra}"

    if level.lower() == "warning":
        logger.warning(final_message)
    elif level.lower() == "error":
        logger.error(final_message)
    else:
        logger.info(final_message)

log_llm("CACHE", f"AI cache version = {AI_CACHE_VERSION}")

class FactCheckController:

    # =========================
    # IMPROVEMENT 1: STAT KEYWORD MAP
    # WHY: Your old build_statistical_key() used a long chain of if/elif blocks
    # that only covered Singapore. This table-driven approach makes it trivial
    # to add any new country — just add one line to the list.
    # =========================
    COUNTRY_CODE_MAP = {
            "singapore": ("Singapore", "SGP"),
            "malaysia": ("Malaysia", "MYS"),
            "indonesia": ("Indonesia", "IDN"),
            "thailand": ("Thailand", "THA"),
            "vietnam": ("Vietnam", "VNM"),
            "philippines": ("Philippines", "PHL"),
            "china": ("China", "CHN"),
            "japan": ("Japan", "JPN"),
            "india": ("India", "IND"),
            "australia": ("Australia", "AUS"),
            "united states": ("United States", "USA"),
            "usa": ("United States", "USA"),
            "america": ("United States", "USA"),
            "united kingdom": ("United Kingdom", "GBR"),
            "uk": ("United Kingdom", "GBR"),
            "britain": ("United Kingdom", "GBR"),
            "germany": ("Germany", "DEU"),
            "france": ("France", "FRA"),
            "brazil": ("Brazil", "BRA"),
            "world": ("Global", "WLD"),
            "global": ("Global", "WLD"),
        }
    
    INDICATOR_MAP = {
        "inflation": ("FP.CPI.TOTL.ZG", "inflation_rate", "%"),
        "cpi": ("FP.CPI.TOTL.ZG", "inflation_rate", "%"),
        "unemployment": ("SL.UEM.TOTL.ZS", "unemployment_rate", "%"),
        "jobless": ("SL.UEM.TOTL.ZS", "unemployment_rate", "%"),
        "gdp growth": ("NY.GDP.MKTP.KD.ZG", "gdp_growth", "%"),
        "economic growth": ("NY.GDP.MKTP.KD.ZG", "gdp_growth", "%"),
        "gdp per capita": ("NY.GDP.PCAP.CD", "gdp_per_capita", "USD"),
        "population": ("SP.POP.TOTL", "population", "people"),
        "life expectancy": ("SP.DYN.LE00.IN", "life_expectancy", "years"),
        "infant mortality": ("SP.DYN.IMRT.IN", "infant_mortality", "per 1000"),
        "vaccination": ("SH.IMM.IDPT", "vaccination_rate", "%"),
        "immunisation": ("SH.IMM.IDPT", "vaccination_rate", "%"),
        "immunization": ("SH.IMM.IDPT", "vaccination_rate", "%"),
        "literacy": ("SE.ADT.LITR.ZS", "literacy_rate", "%"),
        "co2": ("EN.ATM.CO2E.PC", "co2_emissions", "metric tons"),
        "carbon emissions": ("EN.ATM.CO2E.PC", "co2_emissions", "metric tons"),
        "poverty": ("SI.POV.DDAY", "poverty_rate", "%"),
        "exports": ("NE.EXP.GNFS.ZS", "exports_gdp", "%"),
        "trade": ("NE.EXP.GNFS.ZS", "exports_gdp", "%"),
    }
    
    # STAT_KEYWORD_MAP = [
    #     # Format: (stat keywords,  country keywords,  metric_key,  country label)
    
    #     # Inflation / CPI
    #     (["inflation", "cpi", "price rise", "cost of living"], ["singapore"],                               "singapore_inflation_rate",    "Singapore"),
    #     (["inflation", "cpi", "price rise", "cost of living"], ["malaysia"],                                "malaysia_inflation_rate",     "Malaysia"),
    #     (["inflation", "cpi", "price rise", "cost of living"], ["united states", "america", "us ", "usa"], "usa_inflation_rate",          "United States"),
    #     (["inflation", "cpi", "price rise", "cost of living"], ["china"],                                   "china_inflation_rate",        "China"),
    #     (["inflation", "cpi", "price rise", "cost of living"], ["uk", "britain", "united kingdom"],         "uk_inflation_rate",           "United Kingdom"),
    #     (["inflation", "cpi", "price rise", "cost of living"], ["world", "global"],                         "global_inflation_rate",       "Global"),
    #     (["inflation", "cpi", "price rise", "cost of living"], ["indonesia"], "indonesia_inflation_rate", "Indonesia"),
    
    #     # Unemployment / jobless
    #     (["unemployment", "jobless", "out of work"],           ["singapore"],                               "singapore_unemployment_rate", "Singapore"),
    #     (["unemployment", "jobless", "out of work"],           ["malaysia"],                                "malaysia_unemployment_rate",  "Malaysia"),
    #     (["unemployment", "jobless", "out of work"],           ["united states", "america", "us ", "usa"], "usa_unemployment_rate",       "United States"),
    #     (["unemployment", "jobless", "out of work"],           ["china"],                                   "china_unemployment_rate",     "China"),
    #     (["unemployment", "jobless", "out of work"],           ["world", "global"],                         "global_unemployment_rate",    "Global"),
    #     (["unemployment", "jobless", "out of work"], ["indonesia"], "indonesia_unemployment_rate", "Indonesia"),
    
    #     # GDP growth
    #     (["gdp", "gdp growth", "economic growth", "economy grew"],  ["singapore"],                               "singapore_gdp_growth",        "Singapore"),
    #     (["gdp", "gdp growth", "economic growth", "economy grew"],  ["malaysia"],                                "malaysia_gdp_growth",          "Malaysia"),
    #     (["gdp", "gdp growth", "economic growth", "economy grew"],  ["united states", "america", "us ", "usa"], "usa_gdp_growth",               "United States"),
    #     (["gdp", "gdp growth", "economic growth", "economy grew"],  ["china"],                                   "china_gdp_growth",             "China"),
    #     (["gdp", "gdp growth", "economic growth", "economy grew"],  ["uk", "britain", "united kingdom"],         "uk_gdp_growth",                "United Kingdom"),
    #     (["gdp", "gdp growth", "economic growth", "economy grew"],  ["world", "global"],                         "global_gdp_growth",            "Global"),
    #     (["gdp", "gdp growth", "economic growth", "economy grew"], ["indonesia"], "indonesia_gdp_growth", "Indonesia"),
    
    #     # GDP per capita
    #     (["gdp per capita", "income per person", "per capita income"], ["singapore"],                               "singapore_gdp_per_capita",    "Singapore"),
    #     (["gdp per capita", "income per person", "per capita income"], ["malaysia"],                                "malaysia_gdp_per_capita",     "Malaysia"),
    #     (["gdp per capita", "income per person", "per capita income"], ["united states", "america", "us ", "usa"], "usa_gdp_per_capita",          "United States"),
    #     (["gdp per capita", "income per person", "per capita income"], ["china"],                                   "china_gdp_per_capita",        "China"),
    #     (["gdp per capita", "income per person", "per capita income"], ["world", "global"],                         "global_gdp_per_capita",       "Global"),
    #     (["gdp per capita", "income per person", "per capita income"], ["indonesia"], "indonesia_gdp_per_capita", "Indonesia"),
    
    #     # Population
    #     (["population", "people", "residents", "citizens"],    ["singapore"],                               "singapore_population",        "Singapore"),
    #     (["population", "people", "residents", "citizens"],    ["malaysia"],                                "malaysia_population",         "Malaysia"),
    #     (["population", "people", "residents", "citizens"],    ["united states", "america", "us ", "usa"], "usa_population",              "United States"),
    #     (["population", "people", "residents", "citizens"],    ["china"],                                   "china_population",            "China"),
    #     (["population", "people", "residents", "citizens"],    ["world", "global"],                         "global_population",           "Global"),
    #     (["population", "people", "residents", "citizens"], ["indonesia"], "indonesia_population", "Indonesia"),
    
    #     # Life expectancy
    #     (["life expectancy", "lifespan", "average age"],       ["singapore"],                               "singapore_life_expectancy",   "Singapore"),
    #     (["life expectancy", "lifespan", "average age"],       ["malaysia"],                                "malaysia_life_expectancy",    "Malaysia"),
    #     (["life expectancy", "lifespan", "average age"],       ["united states", "america", "us ", "usa"], "usa_life_expectancy",         "United States"),
    #     (["life expectancy", "lifespan", "average age"],       ["china"],                                   "china_life_expectancy",       "China"),
    #     (["life expectancy", "lifespan", "average age"],       ["world", "global"],                         "global_life_expectancy",      "Global"),
    #     (["life expectancy", "lifespan", "average age"], ["indonesia"], "indonesia_life_expectancy", "Indonesia"),
    
    #     # Infant mortality
    #     (["infant mortality", "child death", "infant death"],  ["singapore"],                               "singapore_infant_mortality",  "Singapore"),
    #     (["infant mortality", "child death", "infant death"],  ["malaysia"],                                "malaysia_infant_mortality",   "Malaysia"),
    #     (["infant mortality", "child death", "infant death"],  ["world", "global"],                         "global_infant_mortality",     "Global"),
    
    #     # Vaccination
    #     (["vaccination", "immunisation", "immunization", "vaccine rate"], ["singapore"],                    "singapore_vaccination_rate",  "Singapore"),
    #     (["vaccination", "immunisation", "immunization", "vaccine rate"], ["malaysia"],                     "malaysia_vaccination_rate",   "Malaysia"),
    #     (["vaccination", "immunisation", "immunization", "vaccine rate"], ["world", "global"],              "global_vaccination_rate",     "Global"),
    
    #     # Literacy
    #     (["literacy", "literate", "can read"],                 ["singapore"],                               "singapore_literacy_rate",     "Singapore"),
    #     (["literacy", "literate", "can read"],                 ["malaysia"],                                "malaysia_literacy_rate",      "Malaysia"),
    #     (["literacy", "literate", "can read"],                 ["world", "global"],                         "global_literacy_rate",        "Global"),
    
    #     # CO2 / emissions
    #     (["co2", "carbon", "emissions", "carbon footprint"],   ["singapore"],                               "singapore_co2_emissions",     "Singapore"),
    #     (["co2", "carbon", "emissions", "carbon footprint"],   ["malaysia"],                                "malaysia_co2_emissions",      "Malaysia"),
    #     (["co2", "carbon", "emissions", "carbon footprint"],   ["united states", "america", "us ", "usa"], "usa_co2_emissions",           "United States"),
    #     (["co2", "carbon", "emissions", "carbon footprint"],   ["china"],                                   "china_co2_emissions",         "China"),
    #     (["co2", "carbon", "emissions", "carbon footprint"],   ["world", "global"],                         "global_co2_emissions",        "Global"),
    #     (["co2", "carbon", "emissions", "carbon footprint"], ["indonesia"], "indonesia_co2_emissions", "Indonesia"),
    
    #     # Poverty
    #     (["poverty", "poor", "below poverty"],                 ["malaysia"],                                "malaysia_poverty_rate",       "Malaysia"),
    #     (["poverty", "poor", "below poverty"],                 ["world", "global"],                         "global_poverty_rate",         "Global"),
    
    #     # Trade / exports
    #     (["export", "trade"],                                  ["singapore"],                               "singapore_exports_gdp",       "Singapore"),
    #     (["export", "trade"],                                  ["malaysia"],                                "malaysia_exports_gdp",        "Malaysia"),
    # ]

    # =========================
    # IMPROVEMENT 2: TRUSTED DOMAIN LIST
    # WHY: You had no way to assess whether sources cited in an article
    # are credible. This list lets you reward articles that come from or
    # reference known reputable outlets.
    # =========================
    TRUSTED_DOMAINS = {
        "reuters.com", "bbc.com", "bbc.co.uk", "apnews.com",
        "channelnewsasia.com", "straitstimes.com", "todayonline.com",
        "theguardian.com", "nytimes.com", "washingtonpost.com",
        "who.int", "gov.sg", "moh.gov.sg", "mom.gov.sg",
        "worldbank.org", "imf.org", "un.org"
    }

    # # Add this class-level set to FactCheckController:
    # LOW_QUALITY_SOURCES = {
    #     "zerohedge", "zerohedge.com",
    #     "naturalnews", "naturalnews.com",
    #     "infowars", "infowars.com",
    #     "breitbart", "breitbart.com",
    #     "beforeitsnews", "beforeitsnews.com",
    #     "thegatewaypundit", "thegatewaypundit.com",
    #     "worldnewsdailyreport",
    #     "empirenews", "empirenews.net",
    # }

    # MEDIUM_QUALITY_SOURCES = {
    #     "benzinga", "benzinga.com",           # financial, not health/science
    #     "manila times", "manilatimes.net",    # regional, limited fact-check rigor
    #     "dailymail", "dailymail.co.uk",
    #     "nypost", "nypost.com",
    #     "thesun", "thesun.co.uk",
    # }

    # =========================
    # IMPROVEMENT 3: EXPANDED SENSATIONALISM DETECTION
    # WHY: Your old has_strong_claim() had 7 words and didn't feed into
    # the score at all. This replaces it with a proper analyser that
    # returns a penalty score used in calculate_score().
    # =========================
    SENSATIONAL_PHRASES = [
        "shocking", "unbelievable", "you won't believe", "bombshell",
        "explosive", "scandal", "exposed", "cover-up", "cover up",
        "they don't want you to know", "mainstream media won't tell",
        "wake up", "share before deleted", "urgent", "must read",
        "doctors hate", "one weird trick", "secret they", "breaking:",
        "miracle", "destroy", "obliterate", "crush", "slam",
    ]

    ISSUE_CODES = {
        "SENSATIONAL": "SENSATIONAL_WORDING",
        "TIME": "TIME_INCONSISTENCY",
        "STAT_MISMATCH": "STAT_MISMATCH",
        "STAT_YEAR": "YEAR_CLARIFICATION",
        "FACTCHECK": "FACTCHECK_CONFLICT",
        "FRAGMENT": "INCOMPLETE_SENTENCE",
        "ABSOLUTE": "ABSOLUTE_WORDING",
        "AUTHORITY": "ATTRIBUTED_STATEMENT",
        "WEAK_SUPPORT": "WEAK_SUPPORT",
        "OK": "NO_MAJOR_ISSUE",
        "VAGUE": "VAGUE_CLAIM"
    }

    VALID_ISSUE_CODES = set(ISSUE_CODES.values())

    ISSUE_LABELS = {
        "SENSATIONAL_WORDING": "Sensational wording",
        "TIME_INCONSISTENCY": "Possible time inconsistency",
        "STAT_MISMATCH": "Possible statistical mismatch",
        "YEAR_CLARIFICATION": "Year clarification needed",
        "FACTCHECK_CONFLICT": "Claim conflicts with known facts",
        "INCOMPLETE_SENTENCE": "Incomplete sentence",
        "ABSOLUTE_WORDING": "Overly strong wording",
        "ATTRIBUTED_STATEMENT": "Attributed statement",
        "WEAK_SUPPORT": "Weak supporting evidence",
        "VAGUE_CLAIM": "Vague statement",
        "NO_MAJOR_ISSUE": "No major issue"
    }


    # =========================
    # 1. BASIC TEXT UTILITIES
    # =========================
    @staticmethod
    def split_sentences(text):
        doc = nlp(text)
        cleaned = []
        for sent in doc.sents:
            sentence_text = sent.text.strip().strip('", ')
            if sentence_text:
                cleaned.append(sentence_text)
        return cleaned

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
            "i think", "in my opinion", "perhaps", "it seems",
            "i believe", "maybe", "i feel", "i suspect", "arguably",
            "some people say", "many believe"
        ]
        return any(phrase in lower for phrase in opinion_phrases)

    # IMPROVEMENT 4: REPLACED has_strong_claim() WITH analyse_sensationalism()
    # WHY: The old method returned True/False but never affected the score.
    # This version returns a dict with the actual penalty so calculate_score()
    # can use it. Also moved to article-level (called once on full text),
    # not sentence-level, since clickbait usually appears in titles/intros.
    @staticmethod
    def analyse_sensationalism(text):
        lower = text.lower()
        upper_chars = sum(1 for c in text if c.isupper() and c.isalpha())
        alpha_chars = sum(1 for c in text if c.isalpha())
        upper_ratio = upper_chars / max(alpha_chars, 1)

        hits = [p for p in FactCheckController.SENSATIONAL_PHRASES if p in lower]

        penalty = min(len(hits) * 5 + (10 if upper_ratio > 0.3 else 0), 20)

        return {
            "sensational_phrases": hits,
            "upper_ratio": round(upper_ratio, 3),
            "penalty": penalty
        }
    
    @staticmethod
    def is_pure_sensational_claim(sentence):
        lower = sentence.lower()

        hits = [p for p in FactCheckController.SENSATIONAL_PHRASES if p in lower]

        has_concrete_signal = (
            FactCheckController.has_number(sentence)
            or FactCheckController.is_attributed_quote(sentence)
            or any(word in lower for word in [
                "inflation", "cpi", "gdp", "population", "unemployment",
                "jobless", "life expectancy", "vaccination", "covid",
                "virus", "disease", "treatment", "medicine", "drug",
                "confirmed", "announced", "reported", "launched",
                "elected", "appointed", "resigned", "banned"
            ])
        )

        return len(hits) > 0 and not has_concrete_signal

    # IMPROVEMENT 5: NEW — ATTRIBUTED QUOTE DETECTION
    # WHY: Sentences like "PM Lee said X" are a distinct claim type.
    # Fabricated quotes are a common misinformation pattern and your
    # router had no way to identify them specifically.
    @staticmethod
    def is_attributed_quote(sentence):
        lower = sentence.lower()
        quote_verbs = [
            "said", "stated", "claimed", "announced", "confirmed",
            "denied", "told", "declared", "admitted", "warned"
        ]
        has_quote_verb = any(v in lower for v in quote_verbs)
        doc = nlp(sentence)
        has_real_speaker = any(
            ent.label_ in ["PERSON", "ORG"]
            and ent.label_ not in ["DISEASE"]
            and not any(word in ent.text.lower() for word in ["covid", "virus", "cancer", "disease", "vaccine"])
            for ent in doc.ents
        )
        return has_quote_verb and has_real_speaker

    # IMPROVEMENT 6: NEW — SOURCE URL CREDIBILITY CHECK
    # WHY: Articles sometimes cite URLs inline. Checking whether those
    # domains are in your trusted list is a fast, zero-API signal.
    @staticmethod
    def check_source_credibility(text):
        urls = re.findall(r'https?://(?:www\.)?([^/\s]+)', text)
        trusted_found = []
        untrusted_found = []
        for domain in urls:
            domain_clean = domain.lower().strip()
            if any(domain_clean.endswith(t) for t in FactCheckController.TRUSTED_DOMAINS):
                trusted_found.append(domain_clean)
            else:
                untrusted_found.append(domain_clean)
        return {
            "trusted": trusted_found,
            "untrusted": untrusted_found,
            "bonus": min(len(trusted_found) * 3, 10),   # up to +10 for trusted sources
            "penalty": min(len(untrusted_found) * 2, 6)  # small penalty for unknown sources
        }
    
    @staticmethod
    def is_authority_attribution(sentence):
        lower = sentence.lower()

        authority_entities = [
        "police", "ministry", "government", "authority", "court",
        "agency", "officials", "spokesperson", "prosecutors",
        "judge", "judiciary", "parliament", "customs", "immigration",
        "ministry of", "department of", "attorney-general",
        "central bank", "monetary authority", "health ministry",

        # add titles
        "president", "prime minister", "minister", "foreign minister",
        "defence minister", "health minister", "finance minister",
        "secretary", "state department", "white house", "cabinet"
    ]

        attribution_patterns = [
            r"\bpolice said\b",
            r"\bpolice were alerted\b",
            r"\baccording to police\b",
            r"\bthe ministry said\b",
            r"\bgovernment said\b",
            r"\bcourt documents\b",
            r"\bauthorities said\b",
            r"\bofficials said\b",
            r"\bspokesperson said\b",
            r"\bagency said\b",

            # add these
            r"\bpresident .* said\b",
            r"\bprime minister .* said\b",
            r"\bminister .* said\b",
            r"\bthe president said\b",
            r"\bthe prime minister said\b"
        ]

        has_authority = any(a in lower for a in authority_entities)
        has_attribution = any(re.search(p, lower) for p in attribution_patterns)

        # stronger cases like "police said", "ministry confirmed"
        direct_patterns = [
            r"\bpolice said\b",
            r"\bpolice were alerted\b",
            r"\baccording to police\b",
            r"\bthe ministry said\b",
            r"\bgovernment said\b",
            r"\bcourt documents\b",
            r"\bauthorities said\b",
            r"\bofficials said\b",
            r"\bspokesperson said\b",
            r"\bagency said\b"
        ]

        if any(re.search(p, lower) for p in direct_patterns):
            return True

        return has_authority and has_attribution
    
    @staticmethod
    def detect_time_inconsistency(sentence):
        lower = sentence.lower()

        future_markers = ["planned", "scheduled", "expected", "will", "preparing to", "paving the way"]
        past_markers = ["have reported", "has reported", "reported", "witnessed", "observed", "already"]

        has_future = any(m in lower for m in future_markers)
        has_past = any(m in lower for m in past_markers)

        return has_future and has_past
    
    @staticmethod
    def is_market_price_sentence(sentence):
        lower = sentence.lower()

        if any(word in lower for word in [
            "inflation", "cpi", "gdp", "unemployment", "jobless",
            "population", "mortality", "life expectancy", "vaccination"
        ]):
            return False

        asset_keywords = [
            "gold", "silver", "oil", "brent", "crude", "futures", "spot",
            "per ounce", "per barrel", "shares", "stocks", "stock", "index",
            "dow", "nasdaq", "s&p", "bitcoin", "ethereum", "crypto",
            "bond", "bonds", "yield", "commodity", "currencies", "forex"
        ]

        movement_words = [
            "traded", "rose", "fell", "gained", "dropped", "jumped", "slipped",
            "climbed", "declined", "surged", "plunged"
        ]

        has_asset_keyword = any(k in lower for k in asset_keywords)
        has_movement_word = any(k in lower for k in movement_words)
        has_money = bool(re.search(r"(us\$|s\$|\$)\s?\d", lower))
        has_percent = "%" in sentence or "per cent" in lower

        return has_asset_keyword and has_movement_word and (has_money or has_percent)
    
    @staticmethod
    def classify_claim_type(sentence):
        lower = sentence.lower()

        if FactCheckController.is_opinion(sentence):
            return "opinion"

        if FactCheckController.is_pure_sensational_claim(sentence):
            return "sensationalism_only"

        if FactCheckController.is_market_price_sentence(sentence):
            return "market_data"

        if FactCheckController.is_attributed_quote(sentence):
            return "reported_speech"

        if any(word in lower for word in [
            "vaccine", "virus", "disease", "covid", "cancer",
            "treatment", "medicine", "drug", "epidemic", "outbreak",
            "infection", "symptom", "cure", "mortality", "death rate"
        ]):
            return "health_claim"

        if (
            FactCheckController.has_number(sentence)
            and FactCheckController.has_statistical_indicator(sentence)
            and not FactCheckController.is_money_amount_claim(sentence)
        ):
            return "statistical_claim"

        return "general_claim"
    
    @staticmethod
    def is_money_amount_claim(sentence):
        lower = sentence.lower()
        return bool(re.search(
            r"(s\$|us\$|\$|sgd|usd|eur|gbp)\s?\d+(?:\.\d+)?\s*(million|billion|thousand)?",
            lower
        ))

    # =========================
    # 2. ROUTING / CLAIM TYPE
    # =========================
    # @classmethod
    # def route_sentence(cls, sentence):
    #     entities = cls.extract_entities(sentence)
    #     entity_labels = [ent["label"] for ent in entities]
    #     lower = sentence.lower()

    #     check_types = []
    #     reasons = []

    #     if cls.is_opinion(sentence):
    #         return {
    #             "text": sentence,
    #             "route": ["opinion"],
    #             "reason": "This sentence appears to be an opinion.",
    #             "entities": entities
    #         }

    #     # Health claims
    #     if any(word in lower for word in [
    #         "vaccine", "virus", "disease", "covid", "cancer",
    #         "treatment", "medicine", "drug", "epidemic", "outbreak",
    #         "infection", "symptom", "cure", "mortality", "death rate"
    #     ]):
    #         check_types.append("google_factcheck")
    #         reasons.append("Health-related claim detected.")

    #     # Statistical claims
    #     if cls.has_number(sentence):
    #         if any(word in lower for word in [
    #             "inflation", "cpi", "gdp", "population",
    #             "unemployment", "jobless", "mortality", "death rate",
    #             "life expectancy", "infant mortality", "vaccination",
    #             "immunisation", "immunization", "literacy",
    #             "co2", "carbon", "emissions", "poverty", "export", "trade"
    #         ]):
    #             check_types.append("statistical_check")
    #             reasons.append("Official statistical claim detected.")

    #     # IMPROVEMENT 7: QUOTE CHECK ADDED TO ROUTER
    #     # WHY: Attributed quotes need their own route so we can specifically
    #     # search for whether the person actually made that statement.
    #     if cls.is_attributed_quote(sentence):
    #         check_types.append("general_check")
    #         reasons.append("Attributed quote detected — using LLM assessment.")

    #     # Current events / named entities
    #     # if any(word in lower for word in [
    #     #     "announced", "reported", "said", "launched", "won",
    #     #     "attacked", "released", "issued", "today", "yesterday",
    #     #     "this week", "arrested", "signed", "passed", "elected",
    #     #     "appointed", "resigned", "died", "killed", "banned"
    #     # ]) or any(label in entity_labels for label in ["PERSON", "ORG", "GPE", "PRODUCT", "EVENT"]):
    #     #     check_types.append("news_check")
    #     #     reasons.append("Current event or named entity claim detected.")

    #     # Sensationalism flag (doesn't add a route, just annotates)
    #     if cls.has_number(sentence) is False and any(
    #         word in lower for word in ["worst", "best", "always", "never", "definitely", "undeniably"]
    #     ):
    #         reasons.append("Strong absolute wording detected.")

    #     # IMPROVEMENT 8: general_check NOW GOES TO LLM INSTEAD OF DEAD-END
    #     # WHY: Before, general_check did nothing at all. Now it routes to
    #     # the Groq LLM which can handle any claim type not caught above.
    #     if not check_types:
    #         check_types.append("general_check")
    #         reasons.append("General factual claim — will use LLM assessment.")

    #     return {
    #         "text": sentence,
    #         "route": list(dict.fromkeys(check_types)),
    #         "reason": " ".join(reasons),
    #         "entities": entities
    #     }

    @classmethod
    def route_sentence(cls, sentence):
        entities = cls.extract_entities(sentence)
        lower = sentence.lower()

        check_types = []
        reasons = []

        claim_type = cls.classify_claim_type(sentence)

        if claim_type == "opinion":
            return {
                "text": sentence,
                "route": ["opinion"],
                "reason": "This sentence appears to be an opinion.",
                "entities": entities
            }

        if claim_type == "sensationalism_only":
            return {
                "text": sentence,
                "route": ["sensationalism_only"],
                "reason": "Sensationalist language detected.",
                "entities": entities
            }

        if claim_type == "market_data":
            return {
                "text": sentence,
                "route": ["market_data"],
                "reason": "Financial market price movement detected.",
                "entities": entities
            }

        if claim_type == "reported_speech":
            check_types.append("reported_speech")
            reasons.append("Reported statement from a named source.")
            if "general_check" not in check_types:
                check_types.append("general_check")
                reasons.append("Statement content will also be assessed for plausibility.")

        if cls.is_authority_attribution(sentence):
            check_types.append("authority_source")
            reasons.append("Reported information attributed to an official authority.")
            if "general_check" not in check_types:
                check_types.append("general_check")
                reasons.append("Authority-attributed content will also be assessed for plausibility.")

        if claim_type == "health_claim":
            check_types.append("google_factcheck")
            reasons.append("Health-related claim detected.")
            if "general_check" not in check_types:
                check_types.append("general_check")
                reasons.append("Health claim will also be assessed for plausibility.")

        if claim_type == "statistical_claim":
            check_types.append("statistical_check")
            reasons.append("Official statistical claim detected.")

        if not cls.has_number(sentence) and any(
            word in lower for word in ["worst", "best", "always", "never", "definitely", "undeniably"]
        ):
            reasons.append("Strong absolute wording detected.")

        if (
            cls.has_number(sentence)
            and cls.has_statistical_indicator(sentence)
            and not cls.is_money_amount_claim(sentence)
            and "statistical_check" not in check_types
        ):
            check_types.append("statistical_check")
            reasons.append("Official statistical claim detected.")

        if not any(r in check_types for r in [
            "google_factcheck",
            "statistical_check",
            "general_check"
        ]):
            check_types.append("general_check")
            reasons.append("General factual claim — will use LLM assessment.")

        return {
            "text": sentence,
            "route": list(dict.fromkeys(check_types)),
            "reason": " ".join(reasons),
            "entities": entities
        }

    # =========================
    # 3. NEWS QUERY + FILTERING
    # =========================
    # @staticmethod
    # def build_news_query(sentence):
    #     doc = nlp(sentence)
    #     keywords = []
    #     allowed_entity_labels = {"ORG", "PERSON", "GPE", "PRODUCT", "EVENT"}
    #     allowed_action_lemmas = {
    #         "announce", "launch", "release", "win",
    #         "attack", "report", "issue", "arrest", "sign", "ban"
    #     }
    #     ignore_words = {
    #         "yesterday", "today", "tomorrow",
    #         "week", "month", "year", "last", "new"
    #     }

    #     for ent in doc.ents:
    #         if ent.label_ in allowed_entity_labels:
    #             keywords.append(ent.text)

    #     for token in doc:
    #         word = token.text.lower()
    #         lemma = token.lemma_.lower()
    #         if token.is_stop or token.is_punct or word in ignore_words:
    #             continue
    #         if token.pos_ in {"NOUN", "PROPN"} and len(token.text) > 2:
    #             keywords.append(token.text)
    #         elif lemma in allowed_action_lemmas:
    #             keywords.append(lemma)

    #     cleaned_keywords = []
    #     seen = set()
    #     for word in keywords:
    #         word_clean = word.strip()
    #         if word_clean and word_clean.lower() not in seen:
    #             cleaned_keywords.append(word_clean)
    #             seen.add(word_clean.lower())

    #     return " ".join(cleaned_keywords[:5]) if cleaned_keywords else sentence

    # @staticmethod
    # def build_news_query(sentence):
    #     doc = nlp(sentence)
    #     keywords = []

    #     allowed_entity_labels = {"ORG", "PERSON", "GPE", "PRODUCT", "EVENT"}
    #     allowed_action_lemmas = {
    #         "announce", "launch", "release", "win",
    #         "attack", "report", "issue", "arrest", "sign", "ban"
    #     }
    #     # In build_news_query, expand ignore_words:
    #     ignore_words = {
    #         "yesterday", "today", "tomorrow", "week", "month",
    #         "year", "last", "new", "according", "show", "say",
    #         "develop", "rate", "term", "effect", "individual",
    #         # Add these:
    #         "study", "studies", "research", "report", "claim",
    #         "suggest", "find", "found", "show", "evidence",
    #         "people", "person", "group", "data", "result"
    #     }

    #     # Track which tokens are part of a percentage so we handle them together
    #     percentage_indices = set()
    #     for i, token in enumerate(doc):
    #         if token.like_num and i + 1 < len(doc):
    #             next_tok = doc[i + 1]
    #             if next_tok.text in {"%", "percent", "per cent"}:
    #                 percentage_indices.add(i)
    #                 percentage_indices.add(i + 1)

    #     # Named entities first
    #     for ent in doc.ents:
    #         if ent.label_ in allowed_entity_labels:
    #             keywords.append(ent.text)

    #     for token in doc:
    #         word = token.text.lower()
    #         lemma = token.lemma_.lower()

    #         if token.is_stop or token.is_punct or word in ignore_words:
    #             continue

    #         # Skip tokens that are part of a percentage — don't include the number
    #         # or the % sign themselves, just let the surrounding nouns carry the meaning
    #         if token.i in percentage_indices:
    #             continue

    #         # Skip all other bare numbers
    #         if token.like_num or token.pos_ == "NUM":
    #             continue

    #         if token.pos_ in {"NOUN", "PROPN"} and len(token.text) > 3:
    #             keywords.append(token.text)
    #         elif lemma in allowed_action_lemmas:
    #             keywords.append(lemma)

    #     seen = set()
    #     cleaned = []
    #     for word in keywords:
    #         w = word.strip()
    #         if w and w.lower() not in seen:
    #             cleaned.append(w)
    #             seen.add(w.lower())

    #     return " ".join(cleaned[:6]) if cleaned else sentence

    # # @staticmethod
    # # def is_relevant_article(claim_text, article):
    # #     title = (article.get("title") or "").lower()
    # #     description = (article.get("description") or "").lower()
    # #     combined = title + " " + description

    # #     important_terms = []
    # #     doc = nlp(claim_text)
    # #     for ent in doc.ents:
    # #         important_terms.append(ent.text.lower())
    # #     for token in doc:
    # #         if token.pos_ in {"NOUN", "PROPN"} and not token.is_stop and len(token.text) > 2:
    # #             important_terms.append(token.text.lower())

    # #     important_terms = list(dict.fromkeys(important_terms))
    # #     match_count = sum(1 for term in important_terms if term in combined)
    # #     return match_count >= 1 and len(important_terms) >= 1

    # @staticmethod
    # def is_relevant_article(claim_text, article):
    #     title = (article.get("title") or "").lower()
    #     description = (article.get("description") or "").lower()
    #     combined = title + " " + description

    #     doc = nlp(claim_text)

    #     # Named entities are the strongest signal — extract these separately
    #     named_entities = [
    #         ent.text.lower() for ent in doc.ents
    #         if ent.label_ in {"ORG", "PERSON", "GPE", "PRODUCT", "EVENT", "FAC", "LOC"}
    #     ]

    #     # General keywords — nouns and meaningful verbs only, no stop words
    #     keywords = [
    #         token.text.lower() for token in doc
    #         if not token.is_stop and not token.is_punct
    #         and token.pos_ in {"NOUN", "PROPN"} and len(token.text) > 3
    #     ]

    #     all_terms = list(dict.fromkeys(named_entities + keywords))

    #     if not all_terms:
    #         return False

    #     # Count how many terms appear in the article
    #     matched_terms = [term for term in all_terms if term in combined]
    #     match_count = len(matched_terms)

    #     # Named entity match — strongest signal
    #     # If the claim mentions Singapore, WHO, Pfizer etc and the article does too, that's meaningful
    #     entity_match_count = sum(1 for ent in named_entities if ent in combined)

    #     # How much of the claim's vocabulary appears in the article (0.0 to 1.0)
    #     coverage = match_count / len(all_terms)

    #     # Relevance rules — from strongest to weakest:
    #     # 1. At least one named entity matches AND at least 2 keywords match
    #     if entity_match_count >= 1 and match_count >= 3:
    #         return True

    #     # 2. No named entities in claim (generic claim) but strong keyword overlap
    #     if not named_entities and match_count >= 3 and coverage >= 0.4:
    #         return True

    #     # 3. Multiple named entities all match (very strong signal even with few keywords)
    #     if entity_match_count >= 2:
    #         return True

    #     return False
    
    # @staticmethod
    # def is_quality_source(article):
    #     return FactCheckController.get_source_quality(article) != "low"
    
    # @staticmethod
    # def get_source_quality(article):
    #     source = (article.get("source_name") or "").lower()

    #     if any(bad in source for bad in FactCheckController.LOW_QUALITY_SOURCES):
    #         return "low"

    #     if any(mid in source for mid in FactCheckController.MEDIUM_QUALITY_SOURCES):
    #         return "medium"

    #     return "high"
    
    # @staticmethod
    # def is_recent_claim(sentence):
    #     """
    #     Detects if a claim is explicitly about recent events.
    #     If yes, news search will be restricted to recent articles only.
    #     If no, we don't restrict by date — the claim could be historical.
    #     """
    #     lower = sentence.lower()
    #     recent_words = [
    #         "today", "yesterday", "this week", "this month",
    #         "recently", "just", "latest", "breaking", "now",
    #         "announced", "launched", "released", "confirmed",
    #         "just announced", "hours ago", "days ago"
    #     ]
    #     return any(word in lower for word in recent_words)

    # @staticmethod
    # def assess_news_support(claim_text, relevant_articles):
    #     if not relevant_articles:
    #         return "none"

    #     strong_terms = []
    #     doc = nlp(claim_text)
    #     for ent in doc.ents:
    #         strong_terms.append(ent.text.lower())
    #     for token in doc:
    #         if token.pos_ in {"NOUN", "PROPN"} and not token.is_stop and len(token.text) > 2:
    #             strong_terms.append(token.text.lower())
    #     strong_terms = list(dict.fromkeys(strong_terms))

    #     strong_match_count = 0
    #     for article in relevant_articles:
    #         title = (article.get("title") or "").lower()
    #         description = (article.get("description") or "").lower()
    #         combined = title + " " + description
    #         overlap = sum(1 for term in strong_terms if term in combined)
    #         if overlap >= 2:
    #             strong_match_count += 1

    #     if strong_match_count >= 3:
    #         return "strong"
    #     elif strong_match_count >= 2:
    #         return "moderate"
    #     elif strong_match_count >= 1:
    #         return "weak"
    #     else:
    #         return "none"

    # # =========================
    # # 4. NEWS PROVIDERS
    # # =========================
    # @staticmethod
    # def lookup_newsapi_evidence(claim_text):
    #     query = FactCheckController.build_news_query(claim_text)
    #     is_recent = FactCheckController.is_recent_claim(claim_text)
    #     cache_key = query + "_recent" if is_recent else query

    #     cached = NewsCache().get_cached_result(query)
    #     if cached:
    #         print("Cache hit (NewsAPI):", query)
    #         return cached

    #     print("Cache miss → calling NewsAPI")
    #     api_key = os.getenv("NEWSAPI_KEY")
    #     if not api_key:
    #         return {"matched": False, "reason": "No NewsAPI key"}

    #     url = "https://newsapi.org/v2/everything"
    #     params = {
    #         "q": query,
    #         "language": "en",
    #         "pageSize": 20,
    #         "sortBy": "publishedAt",
    #         "apiKey": api_key
    #     }

    #     if FactCheckController.is_recent_claim(claim_text):
    #         since_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    #         params["from"] = since_date

    #     try:
    #         response = requests.get(url, params=params, timeout=10)
    #         response.raise_for_status()
    #         data = response.json()
    #         articles = data.get("articles", [])

    #         formatted_articles = [
    #             {
    #                 "title": a.get("title"),
    #                 "description": a.get("description"),
    #                 "source_name": a.get("source", {}).get("name")
    #             }
    #             for a in articles
    #         ]

    #         formatted_articles = [a for a in formatted_articles if FactCheckController.is_quality_source(a)]

    #         relevant_articles = [
    #             a for a in formatted_articles
    #             if FactCheckController.is_relevant_article(claim_text, a)
    #         ]
            
    #         if not relevant_articles:
    #             result = {
    #                 "matched": False, "provider": "NewsAPI",
    #                 "query_used": query, "articles_found": 0,
    #                 "sources": [], "sample_titles": [], "support_level": "none"
    #             }
    #             NewsCache().save(query, result, "NewsAPI")
    #             return result
            
    #         high_quality_articles = [
    #                         a for a in relevant_articles
    #                         if FactCheckController.get_source_quality(a) == "high"
    #                     ]

    #         medium_quality_articles = [
    #             a for a in relevant_articles
    #             if FactCheckController.get_source_quality(a) == "medium"
    #         ]

    #         sources = list(set(
    #             a.get("source_name", "Unknown")
    #             for a in relevant_articles if a.get("source_name")
    #         ))

    #         support_level = FactCheckController.assess_news_support(claim_text, relevant_articles)
    #         if support_level == "none" and medium_quality_articles:
    #             support_level = "weak"

    #         result = {
    #             "matched": True, "provider": "NewsAPI",
    #             "query_used": query, "articles_found": len(relevant_articles),
    #             "sources": sources,
    #             "sample_titles": [a.get("title", "") for a in relevant_articles[:3]],
    #             "support_level": support_level
    #         }
    #         NewsCache().save(cache_key, result, "NewsAPI")
    #         return result

    #     except Exception as e:
    #         result = {"matched": False, "provider": "NewsAPI", "query_used": query, "error": str(e)}
    #         NewsCache().save(query, result, "NewsAPI")
    #         return result

    # @staticmethod
    # def lookup_newsdata_evidence(claim_text):
    #     api_key = os.getenv("NEWS_DATA_KEY")
    #     if not api_key:
    #         return {"matched": False, "reason": "No NewsData key"}

    #     query = FactCheckController.build_news_query(claim_text)

    #     # IMPROVEMENT 9: NEWSDATA NOW CACHES
    #     # WHY: The original code called NewsData every time with no caching.
    #     # This was burning free-tier quota unnecessarily.
    #     cached = NewsCache().get_cached_result(query + "_newsdata")
    #     if cached:
    #         print("Cache hit (NewsData):", query)
    #         return cached

    #     url = "https://newsdata.io/api/1/latest"
    #     params = {"apikey": api_key, "q": query, "language": "en"}

    #     try:
    #         response = requests.get(url, params=params, timeout=10)
    #         response.raise_for_status()
    #         data = response.json()
    #         articles = data.get("results", [])

    #         articles = [a for a in articles if FactCheckController.is_quality_source(a)]

    #         relevant_articles = [
    #             a for a in articles
    #             if FactCheckController.is_relevant_article(claim_text, a)
    #         ]

    #         if not relevant_articles:
    #             result = {
    #                 "matched": False, "provider": "NewsData",
    #                 "query_used": query, "articles_found": 0,
    #                 "sources": [], "sample_titles": [], "support_level": "none"
    #             }
    #             NewsCache().save(query + "_newsdata", result, "NewsData")
    #             return result

    #         sources = list(set(
    #             a.get("source_name", "Unknown")
    #             for a in relevant_articles if a.get("source_name")
    #         ))
    #         support_level = FactCheckController.assess_news_support(claim_text, relevant_articles)

    #         result = {
    #             "matched": True, "provider": "NewsData",
    #             "query_used": query, "articles_found": len(relevant_articles),
    #             "sources": sources,
    #             "sample_titles": [a.get("title", "") for a in relevant_articles[:3]],
    #             "support_level": support_level
    #         }
    #         NewsCache().save(query + "_newsdata", result, "NewsData")
    #         return result

    #     except Exception as e:
    #         return {"matched": False, "provider": "NewsData", "query_used": query, "error": str(e)}

    # @staticmethod
    # def lookup_news_evidence(claim_text):
    #     return FactCheckController.lookup_newsapi_evidence(claim_text)

    # IMPROVEMENT 10: NEW — QUOTE VERIFICATION
    # WHY: When someone writes "Minister X said crime is up 50%", you need
    # to search specifically for whether that person made that statement,
    # not just whether crime is up. This method extracts the speaker and
    # searches with their name as the primary query term.
    # @staticmethod
    # def lookup_quote_evidence(sentence):
    #     doc = nlp(sentence)

    #     speaker = next(
    #         (ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG"]),
    #         None
    #     )
    #     if not speaker:
    #         return {"matched": False, "reason": "No speaker identified in quote"}

    #     speaker_words = {w.lower() for w in speaker.split()}

    #     quote_verbs = {
    #         "say", "state", "claim", "announce", "confirm",
    #         "deny", "tell", "declare", "admit", "warn"
    #     }

    #     keywords = [speaker]

    #     # add useful verbs
    #     for token in doc:
    #         lemma = token.lemma_.lower()
    #         if token.pos_ == "VERB" and lemma in quote_verbs:
    #             if lemma not in speaker_words:
    #                 keywords.append(lemma)

    #     # add strong entities other than the speaker
    #     for ent in doc.ents:
    #         ent_text = ent.text.strip()
    #         ent_words = {w.lower() for w in ent_text.split()}

    #         if ent.label_ in {"GPE", "ORG", "EVENT", "PRODUCT"}:
    #             if not ent_words.issubset(speaker_words):
    #                 keywords.append(ent_text)

    #     # add important nouns / proper nouns
    #     for token in doc:
    #         word = token.text.strip()
    #         lower_word = word.lower()

    #         if token.is_stop or token.is_punct or len(word) <= 2:
    #             continue

    #         if lower_word in speaker_words:
    #             continue

    #         if token.pos_ in {"NOUN", "PROPN"}:
    #             keywords.append(word)

    #     # deduplicate while preserving order
    #     cleaned = []
    #     seen = set()
    #     for word in keywords:
    #         norm = word.lower()
    #         if norm not in seen:
    #             cleaned.append(word)
    #             seen.add(norm)

    #     query_text = " ".join(cleaned[:6])

    #     result = FactCheckController.lookup_news_evidence(query_text)
    #     result["speaker"] = speaker
    #     result["quote_query"] = query_text
    #     return result

    # =========================
    # 5. GOOGLE FACT CHECK
    # =========================
    @staticmethod
    def lookup_google_fact_check(claim_text):
        cached = FactcheckCache().get_cached_result(claim_text)
        if cached:
            print("Cache hit (Google Fact Check):", claim_text[:60])

            if "ok" not in cached:
                cached["ok"] = True  # assume old cache = success

            return cached

        print("Cache miss → calling Google Fact Check API")
        api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
        if not api_key:
            return {
                "ok": False,
                "matched": False,
                "provider": "google_factcheck",
                "error": "no_api_key",
                "message": "Google Fact Check API key not configured"
            }

        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {"query": claim_text, "key": api_key, "languageCode": "en"}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            claims = data.get("claims", [])

            if not claims:
                result = {
                    "ok": True,
                    "matched": False,
                    "provider": "google_factcheck",
                    "publisher": "",
                    "url": "",
                    "rating": "No rating"
                }
                FactcheckCache().save(claim_text, result)
                return result

            first_claim = claims[0]
            reviews = first_claim.get("claimReview", [])

            if reviews:
                first_review = reviews[0]
                result = {
                    "ok": True,
                    "matched": True,
                    "provider": "google_factcheck",
                    "publisher": first_review.get("publisher", {}).get("name", "Unknown"),
                    "url": first_review.get("url", ""),
                    "rating": first_review.get("textualRating", "No rating")
                }
            else:
                result = {
                    "ok": True,
                    "matched": True,
                    "provider": "google_factcheck",
                    "publisher": "Unknown",
                    "url": "",
                    "rating": "No rating"
                }

            FactcheckCache().save(claim_text, result)
            return result

        except Exception as e:
            return {
                "ok": False,
                "matched": False,
                "provider": "google_factcheck",
                "error": "exception",
                "message": str(e)
            }

    # =========================
    # 6. STATISTICAL CHECK
    # =========================

    # IMPROVEMENT 11: REPLACED IF/ELIF CHAIN WITH TABLE LOOKUP
    # WHY: The old method had one if-block per metric. Adding a new country
    # meant writing 3-4 more if-blocks. The table-driven approach means
    # adding a new country = one new line in STAT_KEYWORD_MAP.
    @staticmethod
    def build_statistical_key(sentence):
        country_info = FactCheckController.detect_country(sentence)
        metric_info = FactCheckController.detect_indicator(sentence)

        if not country_info or not metric_info:
            print(f"[StatCheck] No generic match for: {sentence[:80]}")
            return None

        metric_key = (
            f"{country_info['country'].lower().replace(' ', '_')}_"
            f"{metric_info['metric_suffix']}"
        )

        return {
            "metric_key": metric_key,
            "country": country_info["country"],
            "country_code": country_info["country_code"],
            "indicator_code": metric_info["indicator_code"],
            "unit": metric_info["unit"],
        }

    # IMPROVEMENT 12: FIXED extract_numeric_value TO AVOID GRABBING YEARS
    # WHY: The old regex matched the FIRST number it found. For a sentence
    # like "Singapore's inflation rose 3.2% in 2023", it could grab "2023"
    # instead of "3.2". Now it prefers decimal numbers first, and avoids
    # 4-digit year patterns.
    @staticmethod
    def split_statistical_sentence(sentence):
        lower = sentence.lower()

        if re.search(r"\baged\s+\d+", lower):
            return [sentence]

        if re.search(r"\d{1,2}-year-old", lower):
            return [sentence]

        if re.search(r"\bblock\s+\w+", lower):
            return [sentence]

        if re.search(r"\b\d{1,2}\.\d{2}\s*(am|pm)\b", lower):
            return [sentence]

        if re.search(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", lower):
            return [sentence]

        # safer connectors for normal clause splitting
        connectors = [" while ", ";", " whereas ", " but "]
        has_connector = any(c in lower for c in connectors)

        number_count = len(re.findall(r"\b\d+(?:\.\d+)?%?\b", sentence))
        country_count = sum(
            1 for name in FactCheckController.COUNTRY_CODE_MAP.keys()
            if name in lower
        )

        metric_repeat_pattern = re.compile(
            r'^(.*?)(\b\d+(?:\.\d+)?%?\b.*?\b20\d{2}\b)\s+and\s+(\b\d+(?:\.\d+)?%?\b.*?\b20\d{2}\b.*)$',
            re.IGNORECASE
        )

        match = metric_repeat_pattern.search(sentence)
        if match:
            prefix = match.group(1).strip()
            first = (prefix + match.group(2)).strip(" ,.-")
            second = (prefix + match.group(3)).strip(" ,.-")
            if len(first) >= 12 and len(second) >= 12:
                return [first, second]

        if not has_connector or (number_count < 2 and country_count < 2):
            return [sentence.strip()]

        parts = re.split(r"\bwhile\b|\bwhereas\b|\bbut\b|;", sentence, flags=re.IGNORECASE)

        cleaned_parts = []
        for part in parts:
            part = part.strip(" ,.-")
            if len(part) >= 12:
                cleaned_parts.append(part)

        return cleaned_parts if cleaned_parts else [sentence.strip()]
    
    @staticmethod
    def has_statistical_indicator(sentence):
        lower = sentence.lower()
        indicators = [
            "inflation", "cpi", "gdp", "population",
            "unemployment", "jobless", "mortality", "death rate",
            "life expectancy", "infant mortality", "vaccination",
            "immunisation", "immunization", "literacy",
            "co2", "carbon", "emissions", "poverty", "export", "trade"
        ]
        return any(word in lower for word in indicators)
    
    @staticmethod
    def extract_numeric_value(text):

        text = text.lower()

        # Remove age patterns
        text = re.sub(r"\baged\s+\d+(?:\s+and\s+\d+)?\b", "", text)
        text = re.sub(r"\b\d{1,2}-year-old\b", "", text)

        # Remove date patterns like "Apr 7", "Mar 23", "2024" when they are calendar references
        text = re.sub(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}\b", "", text)
        text = re.sub(r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", "", text)
        text = re.sub(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "", text)
        text = re.sub(r"\b20\d{2}\b", "", text)

        # Remove time patterns
        text = re.sub(r"\b\d{1,2}\.\d{2}\s*(am|pm)\b", "", text)
        text = re.sub(r"\b\d{1,2}\s*(am|pm)\b", "", text)

        # Prefer percentages first
        percent_match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        if percent_match:
            return float(percent_match.group(1))

        # Then find numeric values with optional scale
        match = re.search(r"(\d+(?:\.\d+)?)\s*(million|billion|thousand)?", text)
        if not match:
            return None

        value = float(match.group(1))
        scale = match.group(2)

        if scale == "thousand":
            value *= 1_000
        elif scale == "million":
            value *= 1_000_000
        elif scale == "billion":
            value *= 1_000_000_000

        return value
        
    @staticmethod
    def extract_year(sentence):
        match = re.search(r"\b(20\d{2})\b", sentence)
        return int(match.group(1)) if match else None
    
    @staticmethod
    def is_money_amount_claim(sentence):
        lower = sentence.lower()
        return bool(re.search(
            r"(s\$|us\$|\$|sgd|usd|eur|gbp)\s?\d+(?:\.\d+)?\s*(million|billion|thousand)?",
            lower
        ))

    @staticmethod
    def lookup_statistical_evidence(claim_text):
        stat_info = FactCheckController.build_statistical_key(claim_text)
        claimed_value = FactCheckController.extract_numeric_value(claim_text)
        requested_year = FactCheckController.extract_year(claim_text)

        if not stat_info or claimed_value is None:
            return {
                "ok": False,
                "matched": False,
                "provider": "statistics",
                "result": "no_match",
                "message": "No trusted statistic found"
            }

        stat_entity = TrustedStatistic()
        official_stat = stat_entity.get_stat_by_metric(
            stat_info["metric_key"],
            stat_info["country"],
            requested_year
        )

        # DB miss -> live fallback
        if not official_stat:
            live_stat = FactCheckController.lookup_worldbank_live(claim_text)
            if live_stat and live_stat.get("ok"):
                return live_stat

            return {
                "ok": False,
                "matched": False,
                "provider": "statistics",
                "result": "no_match",
                "message": "No trusted statistic found"
            }

        official_value = float(official_stat["value"])
        official_year = int(official_stat["year"])

        difference = abs(claimed_value - official_value)
        tolerance = max(abs(official_value) * 0.05, 0.1)

        if difference <= tolerance:
            result = "match"
        elif difference <= tolerance * 2:
            result = "close"
        else:
            result = "mismatch"

        year_note = None
        if requested_year and requested_year != official_year:
            year_note = f"Latest available official data is for {official_year}, not {requested_year}"

        return {
            "ok": True,
            "matched": True,
            "provider": "statistics",
            "source": official_stat["source_name"],
            "source_url": official_stat["source_url"],
            "year": official_year,
            "requested_year": requested_year,
            "year_note": year_note,
            "unit": official_stat["unit"],
            "claimed_value": claimed_value,
            "official_value": official_value,
            "result": result,
            "metric_key": stat_info["metric_key"],
            "country": stat_info["country"],
        }
    
    @staticmethod
    def detect_country(sentence):
        lower = sentence.lower()
        for key, (country_name, country_code) in FactCheckController.COUNTRY_CODE_MAP.items():
            if key in lower:
                return {
                    "country": country_name,
                    "country_code": country_code
                }
        return None
    
    @staticmethod
    def detect_indicator(sentence):
        lower = sentence.lower()

        # longer keywords first, so "gdp per capita" is matched before "gdp"
        for keyword in sorted(FactCheckController.INDICATOR_MAP.keys(), key=len, reverse=True):
            if keyword in lower:
                indicator_code, metric_suffix, unit = FactCheckController.INDICATOR_MAP[keyword]
                return {
                    "keyword": keyword,
                    "indicator_code": indicator_code,
                    "metric_suffix": metric_suffix,
                    "unit": unit
                }

        return None


    @staticmethod
    def lookup_worldbank_live(sentence):
        country_info = FactCheckController.detect_country(sentence)
        indicator_info = FactCheckController.detect_indicator(sentence)

        if not country_info or not indicator_info:
            return {
                "ok": False,
                "matched": False,
                "provider": "worldbank_live",
                "error": "no_mapping",
                "message": "No supported country or indicator detected."
            }

        claimed_value = FactCheckController.extract_numeric_value(sentence)
        if claimed_value is None:
            return {
                "ok": False,
                "matched": False,
                "provider": "worldbank_live",
                "error": "no_numeric_value",
                "message": "No numeric value found in the claim."
            }
        requested_year = FactCheckController.extract_year(sentence)

        country_name = country_info["country"]
        country_code = country_info["country_code"]
        indicator_code = indicator_info["indicator_code"]
        unit = indicator_info["unit"]
        metric_suffix = indicator_info["metric_suffix"]

        metric_key = f"{country_name.lower().replace(' ', '_')}_{metric_suffix}"

        url = (
            f"https://api.worldbank.org/v2/country/{country_code}"
            f"/indicator/{indicator_code}?format=json&mrv=5"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list) or len(data) < 2 or not data[1]:
                return {
                    "ok": False,
                    "matched": False,
                    "provider": "worldbank_live",
                    "error": "no_data",
                    "message": "World Bank returned no usable data."
                }

            latest_record = None
            latest_year = -1
            exact_record = None
            year_note = None

            for record in data[1]:
                value = record.get("value")
                year = record.get("date")

                if value is None or year is None:
                    continue

                year_int = int(year)

                if year_int > latest_year:
                    latest_year = year_int
                    latest_record = record

                if requested_year and year_int == requested_year:
                    exact_record = record
                    break

            chosen_record = exact_record if exact_record else latest_record

            if not chosen_record:
                return {
                    "ok": False,
                    "matched": False,
                    "provider": "worldbank_live",
                    "error": "no_record",
                    "message": "No matching World Bank record was found."
                }

            if requested_year and not exact_record:
                year_note = f"Latest available official data is for {latest_year}, not {requested_year}"

            official_value = float(chosen_record["value"])
            official_year = int(chosen_record["date"])

            if unit == "people":
                official_value_rounded = round(official_value, 0)
            else:
                official_value_rounded = round(official_value, 2)

            tolerance = max(abs(official_value) * 0.05, 0.1)
            result = "match" if abs(claimed_value - official_value) <= tolerance else "mismatch"

            year_note = None
            if requested_year and requested_year != official_year:
                year_note = f"Latest available official data is for {official_year}, not {requested_year}"

            try:
                stat_entity = TrustedStatistic()
                stat_entity.upsert_stat(
                    metric_key,
                    country_name,
                    official_year,
                    official_value_rounded,
                    unit,
                    "World Bank (live)",
                    "https://data.worldbank.org/"
                )
                print(f"[LiveStat] Saved to DB: {metric_key} ({country_name}, {official_year})")
            except Exception as db_err:
                print(f"[LiveStat] DB save failed (non-fatal): {db_err}")

            return {
                "ok": True,
                "matched": True,
                "source": "World Bank (live)",
                "source_url": "https://data.worldbank.org/",
                "year": official_year,
                "requested_year": requested_year,
                "year_note": year_note,
                "unit": unit,
                "claimed_value": claimed_value,
                "official_value": official_value_rounded,
                "result": result,
                "metric_key": metric_key,
                "country": country_name,
                "live": True
            }

        except Exception as e:
            print(f"[LiveStat] World Bank fetch failed: {e}")
            return {
                "ok": False,
                "matched": False,
                "provider": "worldbank_live",
                "error": "exception",
                "message": str(e)
            }

    # =========================
    # 7. LLM GENERAL CHECK (NEW)
    # WHY: Before, any sentence that didn't match a specific route type
    # got zero verification — it silently passed through. Now those
    # sentences go to Groq's free Llama 3 API which can assess ANY claim.
    # Get your free key at: https://console.groq.com
    # =========================
    # @staticmethod
    # def lookup_llm_general_check(sentence):
    #     api_key = os.getenv("GROQ_API_KEY")
    #     if not api_key:
    #         print("[LLM] No GROQ_API_KEY set — skipping LLM check")
    #         return None

    #     headers = {
    #         "Authorization": f"Bearer {api_key}",
    #         "Content-Type": "application/json"
    #     }
    #     payload = {
    #         "model": "llama-3.1-8b-instant",
    #         "temperature": 0.1,
    #         "max_tokens": 200,
    #         "response_format": {"type": "json_object"},
    #         "messages": [
    #             {
    #                 "role": "system",
    #                 "content": (
    #                     "You are a professional fact checker. "
    #                     "Return a JSON object with keys: "
    #                     "verdict, confidence, reason."
    #                 )
    #             },
    #             {
    #                 "role": "user",
    #                 "content": f'Assess whether this claim is factually plausible: "{sentence}"'
    #             }
    #         ]
    #     }

    #     try:
    #         r = requests.post(
    #             "https://api.groq.com/openai/v1/chat/completions",
    #             headers=headers,
    #             json=payload,
    #             timeout=15
    #         )

    #         if not r.ok:
    #             print("[LLM] Status:", r.status_code)
    #             print("[LLM] Response body:", r.text)
    #             return {
    #                 "verdict": "Uncertain",
    #                 "confidence": 0.5,
    #                 "reason": f"Groq API error {r.status_code}: {r.text}"
    #             }

    #         data = r.json()
    #         raw = data["choices"][0]["message"]["content"]
    #         return json.loads(raw)
        
    #     except Exception as e:
    #         print(f"[LLM] Groq call failed: {e}")
    #         return {"verdict": "Uncertain", "confidence": 0.5, "reason": str(e)}

    @staticmethod
    def check_category_match(title, content, selected_category, available_categories):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {
                "ok": False,
                "matched": None,
                "suggested_category": None,
                "confidence": 0,
                "reason": "AI category check is unavailable."
            }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""
            You are checking whether a news article is submitted correctly.

            Selected category:
            {selected_category}

            Available categories:
            {", ".join(available_categories)}

            Article title:
            {title}

            Article content:
            {content[:3000]}

            Return only valid JSON:
            {{
            "matched": true,
            "title_matched": true,
            "suggested_category": "one category from available categories",
            "confidence": 0.85,
            "reason": "short explanation"
            }}

            Rules:
            - "matched" checks whether the selected category fits the article content.
            - "title_matched" checks whether the title fits the article content.
            - If the selected category does not fit, set "matched" to false.
            - If the title and content discuss different topics, set "title_matched" to false.
            - "suggested_category" must be one category from the available categories.
            - Do not invent categories.
            - In the reason, mention both issues if both category and title are mismatched.
            - Keep the reason short and user-friendly.
        """

        payload = {
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.1,
            "max_completion_tokens": 200,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": "You are a news category classification assistant. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            r.raise_for_status()

            raw = r.json()["choices"][0]["message"]["content"].strip()
            parsed = json.loads(raw)

            suggested = parsed.get("suggested_category")
            if suggested not in available_categories:
                suggested = selected_category

            return {
                "ok": True,
                "matched": bool(parsed.get("matched")),
                "suggested_category": suggested,
                "confidence": float(parsed.get("confidence", 0)),
                "reason": parsed.get("reason", "No reason provided."),
                "title_matched": bool(parsed.get("title_matched", True)),
            }

        except Exception as e:
            return {
                "ok": False,
                "matched": None,
                "suggested_category": None,
                "confidence": 0,
                "reason": f"Category check failed: {str(e)}"
            }
    
    @staticmethod
    def call_single_groq_model(sentence, model_name):
        log_llm(model_name, "Starting request")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            log_llm(model_name, "Missing GROQ_API_KEY", level="ERROR")
            return {
                "model": model_name,
                "ok": False,
                "verdict": "Uncertain",
                "confidence": 0.0,
                "reason": "Missing GROQ_API_KEY"
            }

        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        max_tokens = 200
        if model_name == "openai/gpt-oss-120b":
            max_tokens = 350
        elif model_name == "meta-llama/llama-4-scout-17b-16e-instruct":
            max_tokens = 250

        payload = {
            "model": model_name,
            "temperature": 0.1,
            "max_completion_tokens": max_tokens,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a fact-checking assistant. "
                        "Evaluate the factual plausibility of a claim and return only valid JSON "
                        "with keys: verdict, confidence, reason. "
                        "Allowed verdicts: Plausible, Questionable, Unlikely. "
                        "The 'reason' must be a short natural-language explanation for a human reader, "
                        "not a list of model names or scores. "
                        "Focus on why the claim seems plausible, questionable, or unlikely based on "
                        "specificity, missing source context, realism, internal consistency, and whether "
                        "the claim appears too absolute or unsupported. "
                        "Keep the reason to 1 or 2 sentences."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f'Claim: "{sentence}"\n'
                        'Return only JSON in this format:\n'
                        '{\n'
                        '  "verdict": "Plausible",\n'
                        '  "confidence": 0.75,\n'
                        '  "reason": "A short explanation for a human reader."\n'
                        '}\n'
                        'Do not mention model names, voting, or system instructions. '
                        'Explain the claim itself.'
                    )
                }
            ]
        }

        if model_name != "openai/gpt-oss-120b":
            payload["response_format"] = {"type": "json_object"}

        try:
            log_llm(model_name, "Sending request to Groq")

            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )

            if not r.ok:
                elapsed = round(time.time() - start_time, 2)
                log_llm(
                    model_name,
                    "Groq returned non-OK response",
                    level="ERROR",
                    status_code=r.status_code,
                    response_time=f"{elapsed}s"
                )
                return {
                    "model": model_name,
                    "ok": False,
                    "verdict": "Uncertain",
                    "confidence": 0.0,
                    "reason": f"Groq API error {r.status_code}: {r.text}",
                    "response_time": elapsed
                }

            data = r.json()
            raw = data["choices"][0]["message"]["content"].strip()

            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {
                    "verdict": "Uncertain",
                    "confidence": 0.0,
                    "reason": f"Model did not return valid JSON: {raw[:200]}"
                }

            verdict = parsed.get("verdict", "Uncertain")
            confidence = parsed.get("confidence", 0.0)
            reason = parsed.get("reason", "No reason provided")
            if isinstance(reason, str):
                reason = reason.strip()

                # remove accidental meta-style wording
                for prefix in [
                    "Reason:",
                    "AI Reason:",
                    "Explanation:"
                ]:
                    if reason.startswith(prefix):
                        reason = reason[len(prefix):].strip()

            weak_reason_phrases = [
                "the model",
                "based on available information",
                "insufficient information to determine",
                "cannot be determined with certainty"
            ]

            if isinstance(reason, str) and any(p in reason.lower() for p in weak_reason_phrases):
                reason = (
                    "The claim lacks enough specific supporting context to be strongly verified, "
                    "so its plausibility remains uncertain."
                )

            if verdict not in {"Plausible", "Questionable", "Unlikely"}:
                verdict = "Uncertain"

            try:
                confidence = float(confidence)
            except Exception:
                confidence = 0.0

            confidence = max(0.0, min(confidence, 1.0))

            elapsed = round(time.time() - start_time, 2)
            log_llm(
                model_name,
                "Completed successfully",
                verdict=verdict,
                confidence=round(confidence, 2),
                response_time=f"{elapsed}s"
            )

            return {
                "model": model_name,
                "ok": True,
                "verdict": verdict,
                "confidence": confidence,
                "reason": reason,
                "response_time": elapsed
            }

        except requests.exceptions.Timeout:
            elapsed = round(time.time() - start_time, 2)
            log_llm(
                model_name,
                "Request timed out",
                level="WARN",
                response_time=f"{elapsed}s"
            )
            return {
                "model": model_name,
                "ok": False,
                "verdict": "Uncertain",
                "confidence": 0.5,
                "reason": "Model response timed out",
                "response_time": elapsed
            }

        except requests.exceptions.ConnectionError:
            elapsed = round(time.time() - start_time, 2)
            log_llm(
                model_name,
                "Connection error",
                level="ERROR",
                response_time=f"{elapsed}s"
            )
            return {
                "model": model_name,
                "ok": False,
                "verdict": "Uncertain",
                "confidence": 0.5,
                "reason": "Connection error",
                "response_time": elapsed
            }

        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            log_llm(
                model_name,
                "Request failed",
                level="ERROR",
                error=str(e),
                response_time=f"{elapsed}s"
            )
            return {
                "model": model_name,
                "ok": False,
                "verdict": "Uncertain",
                "confidence": 0.5,
                "reason": str(e),
                "response_time": elapsed
            }


    @staticmethod
    def merge_llm_results(model_results):
        weights = {
            "llama-3.3-70b-versatile": 0.4,
            "openai/gpt-oss-120b": 0.4,
            "meta-llama/llama-4-scout-17b-16e-instruct": 0.2
        }

        verdict_scores = {
            "Plausible": 1.0,
            "Questionable": 0.0,
            "Unlikely": -1.0,
            "Uncertain": 0.0
        }

        usable = [
            r for r in model_results
            if isinstance(r, dict)
            and r.get("ok")
            and r.get("confidence", 0) > 0
            and r.get("verdict") in {"Plausible", "Questionable", "Unlikely"}
        ]

        if len(usable) == 0:
            return {
                "verdict": "Uncertain",
                "confidence": 0.0,
                "reason": "The claim could not be reliably assessed because all AI checks failed.",
                "models_used": model_results,
                "usable_model_count": 0,
                "has_disagreement": False,
                "agreement_level": "none",
                "verdict_counts": {
                    "Plausible": 0,
                    "Questionable": 0,
                    "Unlikely": 0
                }
            }

        if len(usable) == 1:
            only = usable[0]
            return {
                "verdict": only["verdict"],
                "confidence": round(float(only.get("confidence", 0.0)) * 0.85, 2),
                "reason": only.get(
                    "reason",
                    "Only one AI model returned a usable result, so the assessment is less certain."
                ),
                "models_used": model_results,
                "usable_model_count": 1,
                "has_disagreement": False,
                "agreement_level": "single_model",
                "verdict_counts": {
                    "Plausible": 1 if only["verdict"] == "Plausible" else 0,
                    "Questionable": 1 if only["verdict"] == "Questionable" else 0,
                    "Unlikely": 1 if only["verdict"] == "Unlikely" else 0
                }
            }

        weighted_sum = 0.0
        weighted_confidence = 0.0
        total_weight = 0.0

        verdict_counts = {
            "Plausible": 0,
            "Questionable": 0,
            "Unlikely": 0
        }

        reasons_by_verdict = {
            "Plausible": [],
            "Questionable": [],
            "Unlikely": []
        }

        for result in usable:
            model = result.get("model", "unknown_model")
            verdict = result.get("verdict", "Uncertain")
            confidence = float(result.get("confidence", 0.0))
            reason = (result.get("reason") or "").strip()

            weight = weights.get(model, 0.2)
            score = verdict_scores.get(verdict, 0.0)

            weighted_sum += score * weight
            weighted_confidence += confidence * weight
            total_weight += weight
            verdict_counts[verdict] += 1

            if reason:
                reasons_by_verdict[verdict].append({
                    "reason": reason,
                    "confidence": confidence,
                    "weight": weight,
                    "model": model
                })

        if total_weight == 0:
            return {
                "verdict": "Uncertain",
                "confidence": 0.0,
                "reason": "No valid weighted AI output was available.",
                "models_used": model_results,
                "usable_model_count": len(usable),
                "has_disagreement": False,
                "agreement_level": "none",
                "verdict_counts": verdict_counts
            }

        avg_score = weighted_sum / total_weight
        avg_confidence = max(0.0, min(weighted_confidence / total_weight, 1.0))

        if verdict_counts["Unlikely"] >= 2:
            final_verdict = "Unlikely"
        elif verdict_counts["Plausible"] >= 2:
            final_verdict = "Plausible"
        elif avg_score <= -0.35:
            final_verdict = "Unlikely"
        elif avg_score >= 0.35:
            final_verdict = "Plausible"
        else:
            final_verdict = "Questionable"

        distinct_verdicts = len({r["verdict"] for r in usable})
        has_disagreement = distinct_verdicts > 1

        if distinct_verdicts == 1:
            agreement_level = "full"
        elif distinct_verdicts == 2:
            agreement_level = "minor"
        else:
            agreement_level = "mixed"

        # pick the best human-readable reason from the winning verdict
        candidate_reasons = reasons_by_verdict.get(final_verdict, [])

        if candidate_reasons:
            best_reason = max(
                candidate_reasons,
                key=lambda x: (x["confidence"], x["weight"])
            )["reason"]
        else:
            if final_verdict == "Plausible":
                best_reason = "The claim appears realistic and internally consistent, although stronger evidence would improve confidence."
            elif final_verdict == "Questionable":
                best_reason = "The claim may be possible, but it lacks enough clear supporting context to be treated as reliable."
            else:
                best_reason = "The claim appears doubtful because it lacks convincing support or seems inconsistent with typical factual reporting."

        if has_disagreement:
            if agreement_level == "minor":
                best_reason += " There was minor disagreement across the AI models."
            else:
                best_reason += " There was mixed disagreement across the AI models."

        return {
            "verdict": final_verdict,
            "confidence": round(avg_confidence, 2),
            "reason": best_reason,
            "models_used": model_results,
            "usable_model_count": len(usable),
            "has_disagreement": has_disagreement,
            "agreement_level": agreement_level,
            "verdict_counts": verdict_counts
        }

    @staticmethod
    def lookup_llm_general_check(sentence):
        cache = LLMCache()

        cached_result = cache.get_cached_result(sentence, version=AI_CACHE_VERSION)
        if cached_result:
            log_llm("CACHE", "LLM verdict cache hit", sentence=sentence[:80])
            return cached_result

        log_llm("CACHE", "LLM verdict cache miss", sentence=sentence[:80])

        lower = sentence.lower()

        high_risk_keywords = [
            "killed", "died", "arrested", "fraud", "scandal", "corruption",
            "cancer", "virus", "vaccine", "war", "attack", "explosion",
            "government", "minister", "president", "prime minister"
        ]

        is_high_risk = any(word in lower for word in high_risk_keywords)

        primary_models = [
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b"
        ]

        backup_model = "meta-llama/llama-4-scout-17b-16e-instruct"

        if is_high_risk:
            models = primary_models
        else:
            models = [
                "llama-3.3-70b-versatile"
            ]

        # models = [
        #     "llama-3.1-8b-instant",
        #     "meta-llama/llama-4-scout-17b-16e-instruct",
        #     "openai/gpt-oss-120b",
        #     "llama-3.3-70b-versatile"
        # ]

        model_results = []

        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            future_to_model = {
                executor.submit(FactCheckController.call_single_groq_model, sentence, model_name): model_name
                for model_name in models
            }

            for future in as_completed(future_to_model):
                model_name = future_to_model[future]

                try:
                    result = future.result()
                    if result is None:
                        result = {
                            "model": model_name,
                            "ok": False,
                            "verdict": "Uncertain",
                            "confidence": 0.0,
                            "reason": "Model returned no result."
                        }
                except Exception as e:
                    result = {
                        "model": model_name,
                        "ok": False,
                        "verdict": "Uncertain",
                        "confidence": 0.0,
                        "reason": str(e)
                    }

                model_results.append(result)

            usable = [
                r for r in model_results
                if r.get("ok") and r.get("confidence", 0) > 0
            ]

            if len(usable) == 0:
                log_llm("FALLBACK", "Backup model triggered", reason="no usable models or weak consensus")
                # complete failure → must fallback
                backup_result = FactCheckController.call_single_groq_model(sentence, backup_model)
                model_results.append(backup_result)

            elif len(usable) == 1 and is_high_risk:
                log_llm("FALLBACK", "Backup model triggered", reason="no usable models or weak consensus")
                # weak consensus for important claim → reinforce with backup
                backup_result = FactCheckController.call_single_groq_model(sentence, backup_model)
                model_results.append(backup_result)

        merged_result = FactCheckController.merge_llm_results(model_results)
        cache.save(sentence, merged_result, version=AI_CACHE_VERSION)

        log_llm("CACHE", "Stored LLM verdict in DB cache", sentence=sentence[:80])
        return merged_result
        
    @staticmethod
    def generate_sentence_feedback_with_llm(sentence, routed):
        print("[FEEDBACK_LLM] generate_sentence_feedback_with_llm entered", flush=True)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {
                "issue_type": "No feedback available",
                "problem": "AI feedback is not available right now.",
                "hint": "Review the sentence manually or try again later.",
                "better_direction": "Make the sentence clearer and add supporting evidence if needed."
            }

        general_result = routed.get("general_result") or {}
        stats_result = routed.get("statistical_result") or {}
        google_result = routed.get("google_factcheck_result") or {}
        route = routed.get("route", [])

        usable_models = [
            m for m in general_result.get("models_used", [])
            if m.get("ok") and m.get("verdict") in {"Plausible", "Questionable", "Unlikely"}
        ]
        disagreement = len({m.get("verdict") for m in usable_models}) > 1 if usable_models else False

        # Build stable cache input
        cache_input_obj = {
            "sentence": sentence.strip().lower(),
            "route": route,
            "final_verdict": general_result.get("verdict"),
            "final_confidence": general_result.get("confidence"),
            "agreement_level": general_result.get("agreement_level"),
            "has_disagreement": general_result.get("has_disagreement"),
            "stat_result": stats_result.get("result") if stats_result else None,
            "stat_source": stats_result.get("source") if stats_result else None,
            "google_matched": google_result.get("matched") if google_result else False,
            "google_rating": google_result.get("rating") if google_result else None
        }       

        cache_input = json.dumps(cache_input_obj, sort_keys=True)
        cache = AIFeedbackCache()
        print("[FEEDBACK_CACHE] About to check cache", flush=True)
        cached_result = cache.get_cached_result(cache_input, cache_type="llm_feedback", version=AI_CACHE_VERSION, ttl_days=AI_CACHE_TTL_DAYS)
        
        if cached_result:
            log_llm("FEEDBACK_CACHE", "Feedback cache hit", cache_key=AI_CACHE_VERSION, sentence=sentence[:80])
            return cached_result

        print("[FEEDBACK_CACHE] Cache miss, about to call LLM", flush=True)
        log_llm("FEEDBACK_CACHE", "Feedback cache miss", cache_key=AI_CACHE_VERSION, sentence=sentence[:80])

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""
        You are helping a news writer improve a sentence.

        Sentence:
        "{sentence}"

        Checking context:
        - Route: {", ".join(route) if route else "general_check"}
        - Final AI verdict: {general_result.get("verdict", "Unknown")}
        - Final AI confidence: {general_result.get("confidence", 0)}
        - Model disagreement: {"Yes" if disagreement else "No"}
        - Statistical result: {stats_result.get("result", "none")}
        - Statistical source: {stats_result.get("source", "none")}
        - Google fact check matched: {google_result.get("matched", False)}
        - Google fact check rating: {google_result.get("rating", "none")}

        Return only valid JSON with:
        - issue_code
        - issue_type
        - problem
        - hint
        - better_direction

        Rules:
        - Be user-friendly and concise.
        - Keep each field short.
        - Do not sound overly technical.
        - Do not say the sentence is false unless strongly supported.
        - "problem" should describe the main issue or assessment.
        - "hint" should give a light suggestion or direction.
        - "better_direction" should give a more concrete improvement step.
        - Do not make "hint" and "better_direction" say the same thing.
        - If the sentence is mostly okay, give gentle guidance rather than criticism.
        """

        payload = {
            "model": "llama-3.1-8b-instant",
            "temperature": 0.2,
            "max_completion_tokens": 220,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a writing and fact-checking assistant. "
                        "Return only valid JSON with keys: "
                        "issue_code, issue_type, problem, hint, better_direction."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        start_time = time.time()

        try:
            log_llm("FEEDBACK", "Sending feedback request", sentence=sentence[:80])

            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )

            if not r.ok:
                elapsed = round(time.time() - start_time, 2)
                log_llm("FEEDBACK", "Feedback request failed", level="error", status_code=r.status_code, response_time=f"{elapsed}s")

                return {
                    "issue_type": "No feedback available",
                    "problem": f"AI feedback request failed ({r.status_code}).",
                    "hint": "Review the sentence manually or try again later.",
                    "better_direction": "Make the sentence clearer and add evidence where possible."
                }

            data = r.json()
            raw = data["choices"][0]["message"]["content"].strip()

            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {
                    "issue_code": "WEAK_SUPPORT",
                    "issue_type": "No feedback available",
                    "problem": "The AI feedback response could not be read properly.",
                    "hint": "Review the sentence manually.",
                    "better_direction": "Clarify the sentence and add supporting evidence."
                }

            issue_code = parsed.get("issue_code", FactCheckController.ISSUE_CODES["WEAK_SUPPORT"])

            if issue_code not in FactCheckController.VALID_ISSUE_CODES:
                issue_code = FactCheckController.ISSUE_CODES["WEAK_SUPPORT"]

            result = {
                "issue_code": issue_code,
                "issue_type": FactCheckController.ISSUE_LABELS.get(issue_code, "Needs review"),
                "problem": parsed.get(
                    "problem",
                    "The sentence may need verification or clarification."
                ),
                "hint": parsed.get(
                    "hint",
                    "Review the claim carefully and consider adding a reliable source."
                ),
                "better_direction": parsed.get(
                    "better_direction",
                    "Rewrite the sentence with clearer wording and supporting evidence."
                )
            }

            print("[FEEDBACK_CACHE] About to save feedback cache", flush=True)
            print(f"[FEEDBACK_CACHE] cache_input={cache_input[:200]}", flush=True)
            print(f"[FEEDBACK_CACHE] result={result}", flush=True)
            cache.save(cache_input, result, cache_type="llm_feedback", version=AI_CACHE_VERSION)

            elapsed = round(time.time() - start_time, 2)
            log_llm("FEEDBACK", "Stored feedback in DB cache", response_time=f"{elapsed}s", sentence=sentence[:80])

            return result

        except requests.exceptions.Timeout:
            elapsed = round(time.time() - start_time, 2)
            log_llm("FEEDBACK", "Feedback request timed out", level="warning", response_time=f"{elapsed}s")

            return {
                "issue_code": FactCheckController.ISSUE_CODES["WEAK_SUPPORT"],
                "issue_type": "Needs review",
                "problem": "The sentence could not be fully reviewed by the AI service.",
                "hint": "Try again later or review the sentence manually.",
                "better_direction": "Add clear evidence or attribution to strengthen the statement."
            }

        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            log_llm("FEEDBACK", "Feedback request failed", level="error", error=str(e), response_time=f"{elapsed}s")

            return {
                "issue_code": FactCheckController.ISSUE_CODES["WEAK_SUPPORT"],
                "issue_type": "Needs review",
                "problem": "The sentence could not be fully reviewed by the AI service.",
                "hint": "Review the sentence manually or try again later.",
                "better_direction": "Add clear evidence or attribution to strengthen the statement."
            }
    # =========================
    # 8. SCORING
    # =========================

    # IMPROVEMENT 14: SCORE STARTS AT 60 NOT 80
    # WHY: Starting at 80 means an article with no verifiable claims at all
    # scores "High Credibility" by default. That's backwards. Starting at 60
    # (Moderate) means evidence has to actively push the score up.
    @staticmethod
    def calculate_score(results, sensationalism=None, source_credibility=None):
        score = 70
        reasons = []

        llm_penalty_applied = False
        llm_bonus_applied = False
        authority_bonus_applied = False
        market_bonus_applied = False
        factcheck_penalty_applied = False
        factcheck_bonus_applied = False
        stat_penalty_applied = False
        stat_bonus_applied = False

        plausible_reasons = []
        questionable_reasons = []
        unlikely_reasons = []

        plausible_count = sum(
            1 for item in results
            if item.get("general_result") and item["general_result"].get("verdict") == "Plausible"
        )

        questionable_count = sum(
            1 for item in results
            if item.get("general_result") and item["general_result"].get("verdict") == "Questionable"
        )

        unlikely_count = sum(
            1 for item in results
            if item.get("general_result") and item["general_result"].get("verdict") == "Unlikely"
        )

        total_checked = plausible_count + questionable_count + unlikely_count

        def get_scope_prefix(count, total):
            if total == 0:
                return "The article"

            ratio = count / total

            if ratio >= 0.75:
                return "The article"
            elif ratio >= 0.4:
                return "Several parts of the article"
            else:
                return "Some parts of the article"

        for item in results:
            route = item.get("route", [])
            google_result = item.get("google_factcheck_result")
            stats_result = item.get("statistical_result")
            general_result = item.get("general_result")

            if item.get("time_inconsistent"):
                score -= 5
                reasons.append(
                    "Temporal inconsistency detected: the timing of the event may be unclear or conflicting."
                )

            if "opinion" in route:
                continue

            if "market_data" in route:
                if not market_bonus_applied:
                    score += 1
                    reasons.append(
                        "Neutral market update detected; treated as factual reporting rather than a credibility risk."
                    )
                    market_bonus_applied = True
                continue

            has_stat_match = (
                stats_result
                and stats_result.get("ok")
                and stats_result.get("matched")
                and stats_result.get("result") == "match"
            )

            has_stat_close = (
                stats_result
                and stats_result.get("ok")
                and stats_result.get("matched")
                and stats_result.get("result") == "close"
            )

            has_stat_mismatch = (
                stats_result
                and stats_result.get("ok")
                and stats_result.get("matched")
                and stats_result.get("result") == "mismatch"
            )

            has_google_match = (
                google_result
                and google_result.get("ok")
                and google_result.get("matched")
            )

            if has_stat_match and not stat_bonus_applied:
                if stats_result.get("year_note"):
                    score += 8
                    reasons.append(
                        f"Statistical claim is consistent with official data from {stats_result.get('source')}. "
                        f"{stats_result.get('year_note')}"
                    )
                else:
                    score += 10
                    reasons.append(
                        f"Statistical claim matches official data from {stats_result.get('source')}."
                    )
                stat_bonus_applied = True

            elif has_stat_close:
                reasons.append(
                    f"Minor statistical difference detected: claimed {stats_result.get('claimed_value')}, "
                    f"official value {stats_result.get('official_value')}."
                )

            elif has_stat_mismatch and not stat_penalty_applied:
                if stats_result.get("year_note"):
                    score -= 8
                    reasons.append(
                        f"Statistical claim differs from the latest available official data from {stats_result.get('source')}. "
                        f"{stats_result.get('year_note')}"
                    )
                else:
                    score -= 10
                    reasons.append(
                        f"Statistical mismatch detected: claimed {stats_result.get('claimed_value')}, "
                        f"official value {stats_result.get('official_value')} from {stats_result.get('source')}."
                    )
                stat_penalty_applied = True

            if has_google_match:
                rating = (google_result.get("rating") or "").lower()

                false_words = [
                    "false", "misleading", "incorrect", "unsupported",
                    "not true", "pants on fire", "inaccurate", "unfounded",
                    "unlikely", "no evidence", "lacks evidence", "disputed",
                    "unproven", "myth", "exaggerated"
                ]

                true_words = [
                    "true", "correct", "accurate", "verified", "confirmed"
                ]

                if any(word in rating for word in false_words) and not factcheck_penalty_applied:
                    score -= 10
                    reasons.append(
                        f"Published fact-check from {google_result.get('publisher', 'unknown')} rated the claim as "
                        f"'{google_result.get('rating')}'."
                    )
                    factcheck_penalty_applied = True

                elif any(word in rating for word in true_words) and not factcheck_bonus_applied:
                    score += 6
                    reasons.append(
                        f"Published fact-check from {google_result.get('publisher', 'unknown')} rated the claim as "
                        f"'{google_result.get('rating')}'."
                    )
                    factcheck_bonus_applied = True

                elif not factcheck_penalty_applied:
                    score -= 1
                    reasons.append(
                        f"Fact-check source found an unclear or mixed rating: '{google_result.get('rating')}'."
                    )
                    factcheck_penalty_applied = True

            if (
                "reported_speech" in route
                and "authority_source" in route
                and not authority_bonus_applied
                and general_result
                and general_result.get("verdict") == "Plausible"
            ):
                score += 2
                reasons.append(
                    "The statement is clearly attributed to an official authority and appears plausible."
                )
                authority_bonus_applied = True

            elif (
                "authority_source" in route
                and not authority_bonus_applied
                and general_result
                and general_result.get("verdict") == "Plausible"
            ):
                score += 1
                reasons.append(
                    "The information is attributed to an official authority and appears plausible."
                )
                authority_bonus_applied = True

            strong_structured_evidence_exists = (
                has_stat_match
                or has_stat_mismatch
                or has_google_match
            )

            if (
                not strong_structured_evidence_exists
                and general_result
                and general_result.get("verdict")
            ):
                verdict = general_result.get("verdict", "Uncertain")
                conf = float(general_result.get("confidence", 0.5))
                reason_text = general_result.get("reason", "")

                usable_models = [
                    m for m in general_result.get("models_used", [])
                    if m.get("ok") and m.get("verdict") in {"Plausible", "Questionable", "Unlikely"}
                ]

                verdict_set = {m["verdict"] for m in usable_models}
                full_agreement = len(verdict_set) == 1 and len(usable_models) >= 2

                if verdict == "Unlikely" and not llm_penalty_applied:
                    if full_agreement and conf >= 0.85:
                        score -= 6
                    elif conf >= 0.75:
                        score -= 4
                    elif conf >= 0.60:
                        score -= 2
                    else:
                        score -= 1

                    unlikely_reasons.append(reason_text)
                    llm_penalty_applied = True

                elif verdict == "Questionable" and not llm_penalty_applied:
                    if full_agreement and conf >= 0.80:
                        score -= 4
                    else:
                        score -= 3

                    questionable_reasons.append(reason_text)
                    llm_penalty_applied = True

                elif verdict == "Plausible" and not llm_bonus_applied:
                    if full_agreement and conf >= 0.85:
                        score += 8
                    elif conf >= 0.75:
                        score += 6
                    else:
                        score += 4

                    plausible_reasons.append(reason_text)
                    llm_bonus_applied = True

        if plausible_reasons:
            prefix = get_scope_prefix(plausible_count, total_checked)
            verb = "appears" if prefix == "The article" else "appear"
            reasons.append(f"{prefix} {verb} believable. {plausible_reasons[0]}")

        if questionable_reasons:
            prefix = get_scope_prefix(questionable_count, total_checked)
            reasons.append(f"{prefix} may need review. {questionable_reasons[0]}")

        if unlikely_reasons:
            prefix = get_scope_prefix(unlikely_count, total_checked)
            reasons.append(f"{prefix} may be doubtful. {unlikely_reasons[0]}")

        has_verified_evidence_anywhere = any(
            (
                item.get("statistical_result")
                and item["statistical_result"].get("ok")
                and item["statistical_result"].get("result") == "match"
            )
            or (
                item.get("google_factcheck_result")
                and item["google_factcheck_result"].get("ok")
                and item["google_factcheck_result"].get("matched")
                and any(
                    w in (item["google_factcheck_result"].get("rating") or "").lower()
                    for w in ["true", "correct", "accurate", "verified", "confirmed"]
                )
            )
            for item in results
        )

        if sensationalism and sensationalism.get("penalty", 0) > 0 and not has_verified_evidence_anywhere:
            reduced_penalty = min(sensationalism["penalty"], 6)
            score -= reduced_penalty

            if sensationalism.get("sensational_phrases"):
                reasons.append(
                    f"Sensational wording detected: {', '.join(sensationalism['sensational_phrases'][:3])}."
                )

        if source_credibility:
            score += min(source_credibility.get("bonus", 0), 6)
            score -= min(source_credibility.get("penalty", 0), 3)

            if source_credibility.get("trusted"):
                reasons.append(
                    f"Cites trusted sources: {', '.join(source_credibility['trusted'][:3])}."
                )

        if plausible_count >= 3 and unlikely_count <= 1:
            score += 3
            reasons.append("Most analysed sentences appear plausible overall.")

        score = max(0, min(score, 100))
        unique_reasons = list(dict.fromkeys(reasons))

        return score, unique_reasons

    # @staticmethod
    # def get_status(score, reasons=None):
    #     reasons = reasons or []

    #     # detect "no evidence" scenario
    #     insufficient_evidence = any(
    #         "No supporting news evidence found" in r for r in reasons
    #     )

    #     if score >= 80:
    #         return "High Credibility"

    #     elif score >= 60:
    #         return "Moderate Credibility"

    #     elif score >= 40:
    #         if insufficient_evidence:
    #             return "Moderate Credibility (Insufficient Evidence)"
    #         return "Low Credibility"

    #     else:
    #         if insufficient_evidence:
    #             return "Low Credibility (Unverified / Recent News)"
    #         return "High Risk"

    @staticmethod
    def get_status_thresholds():
        rule_entity = CredibilityStatusRule()
        rule = rule_entity.get_active_rule()

        if not rule:
            return {
                "verified_min": 85,
                "highly_credible_min": 75,
                "generally_reliable_min": 65,
                "mixed_min": 50,
                "low_confidence_min": 30,
                "misleading_cutoff": 40
            }

        return {
            "verified_min": float(rule["verifiedMinScore"]),
            "highly_credible_min": float(rule["highlyCredibleMinScore"]),
            "generally_reliable_min": float(rule["generallyReliableMinScore"]),
            "mixed_min": float(rule["mixedMinScore"]),
            "low_confidence_min": float(rule["lowConfidenceMinScore"]),
            "misleading_cutoff": float(rule["misleadingCutoffScore"])
        }

    @staticmethod
    def get_status(score, reasons=None):
        score = max(0, min(score, 100))
        reasons = reasons or []

        thresholds = FactCheckController.get_status_thresholds()

        has_stat_match = any("matches official data" in r.lower() for r in reasons)
        has_stat_mismatch = any(
            "statistical mismatch" in r.lower() or
            "differs from the latest available official data" in r.lower()
            for r in reasons
        )

        has_factcheck_false = any(
            "rated the claim as" in r.lower() and any(
                w in r.lower() for w in [
                    "false", "misleading", "incorrect", "unsupported",
                    "unfounded", "disputed", "unproven", "myth"
                ]
            )
            for r in reasons
        )

        has_factcheck_true = any(
            "rated the claim as" in r.lower() and any(
                w in r.lower() for w in [
                    "true", "correct", "accurate", "verified", "confirmed"
                ]
            )
            for r in reasons
        )

        has_llm_unlikely = any("unlikely" in r.lower() for r in reasons)
        has_llm_questionable = any("questionable" in r.lower() for r in reasons)

        # Strong negative signals
        if has_stat_mismatch or has_factcheck_false:
            if score < thresholds["misleading_cutoff"]:
                return "Potentially Misleading"
            return "Low Confidence"

        # Strong verified signals
        if (has_stat_match or has_factcheck_true) and score >= thresholds["verified_min"]:
            return "Verified"

        # High confidence reporting
        if score >= thresholds["highly_credible_min"]:
            return "Highly Credible"

        # Generally acceptable
        if score >= thresholds["generally_reliable_min"]:
            return "Generally Reliable"

        # Mixed signals
        if score >= thresholds["mixed_min"]:
            if has_llm_unlikely or has_llm_questionable:
                return "Mixed / Needs Verification"
            return "Generally Reliable"

        # Weak credibility
        if score >= thresholds["low_confidence_min"]:
            return "Low Confidence"

        # Very risky
        return "Potentially Misleading"

    # =========================
    # 9. MAIN PIPELINE
    # =========================
    @classmethod
    def analyse_content(cls, content, title=None, selected_category=None, available_categories=None):
        sentences = cls.split_sentences(content)

        sensationalism = cls.analyse_sensationalism(content)
        source_credibility = cls.check_source_credibility(content)

        expanded_sentences = []
        for sentence in sentences:
            clauses = cls.split_statistical_sentence(sentence)
            expanded_sentences.extend(clauses)

        results = []

        for sentence in expanded_sentences:
            clean = sentence.strip()
            if (
                len(clean) < 10
                or clean.endswith(":")
                or clean.isupper()
            ):
                continue

            routed = cls.route_sentence(sentence)

            google_result = None
            stats_result = None
            general_result = None

            if "google_factcheck" in routed["route"]:
                google_result = cls.lookup_google_fact_check(sentence)

            if "statistical_check" in routed["route"]:
                stats_result = cls.lookup_statistical_evidence(sentence)

            general_result = None

            # Only run LLM if no strong evidence exists
            if "general_check" in routed["route"]:

                has_strong_evidence = (
                    (stats_result and stats_result.get("ok") and stats_result.get("matched") and stats_result.get("result") == "match")
                    or
                    (google_result and google_result.get("ok") and google_result.get("matched"))
                )

                if not has_strong_evidence:
                    general_result = cls.lookup_llm_general_check(sentence)

            should_allow_llm_fallback = (
                "general_check" in routed["route"]
                or "statistical_check" in routed["route"]
                or "google_factcheck" in routed["route"]
            )

            if should_allow_llm_fallback and general_result is None:
                run_llm = False

                if "statistical_check" in routed["route"]:
                    if not stats_result or not stats_result.get("ok"):
                        run_llm = True

                if "google_factcheck" in routed["route"]:
                    if not google_result or not google_result.get("ok"):
                        run_llm = True

                if "general_check" in routed["route"]:
                    no_stats = not stats_result or not stats_result.get("ok")
                    no_google = not google_result or not google_result.get("ok")

                    if no_stats and no_google:
                        run_llm = True

                if run_llm:
                    general_result = cls.lookup_llm_general_check(sentence)

            routed["google_factcheck_result"] = google_result
            routed["statistical_result"] = stats_result
            routed["general_result"] = general_result
            routed["time_inconsistent"] = cls.detect_time_inconsistency(sentence)
            routed["feedback"] = cls.generate_sentence_feedback(sentence, routed)
            routed["display"] = cls.build_display_metadata(routed)

            results.append(routed)

        category_result = None

        if title and selected_category and available_categories:
            category_result = cls.check_category_match(
                title,
                content,
                selected_category,
                available_categories
            )

        score, score_reasons = cls.calculate_score(results, sensationalism, source_credibility)

        # ===== CATEGORY & TITLE CHECK IMPACT =====
        if category_result:
            if category_result.get("matched") is False and category_result.get("title_matched") is False:
                score -= 7
                score_reasons.append("Both the selected category and article title may not match the content.")

            else:
                if category_result.get("matched") is False:
                    score -= 3
                    score_reasons.append("Selected category may not match the article content.")

                if category_result.get("title_matched") is False:
                    score -= 4
                    score_reasons.append("Article title may not match the article content.")

        score = max(0, min(score, 100))
        status = cls.get_status(score, score_reasons)

        logger = ClaimVerificationLog()
        for item in results:
            llm_provider = None
            if item.get("general_result"):
                models = item["general_result"].get("models_used", [])
                llm_provider = ", ".join([m["model"] for m in models if m.get("ok")])

            logger.save_log(
                claim_text=item["text"],
                route=", ".join(item.get("route", [])),
                factcheck_provider=(item.get("google_factcheck_result") or {}).get("publisher"),
                stats_source=(item.get("statistical_result") or {}).get("source"),
                llm_provider=llm_provider,
                score=score,
                status=status
            )

        return {
            "score": score,
            "status": status,
            "reasons": score_reasons,
            "sensationalism": sensationalism,
            "source_credibility": source_credibility,
            "sentences": results,
            "category_check": category_result,
        }
    
    @staticmethod
    def generate_sentence_feedback(sentence, routed):
        lower = sentence.lower()

        route = routed.get("route", [])
        stats_result = routed.get("statistical_result")
        google_result = routed.get("google_factcheck_result")
        general_result = routed.get("general_result")
        time_inconsistent = routed.get("time_inconsistent", False)

        print(f"[FEEDBACK] generate_sentence_feedback called for: {sentence}", flush=True)
        print(f"[FEEDBACK] route={route}", flush=True)
        print(f"[FEEDBACK] general_verdict={(general_result or {}).get('verdict')}", flush=True)

        vague_words = [
            "many", "some", "experts", "people", "others",
            "significant", "major", "huge", "rapidly", "soon",
            "improve", "better", "worse", "effective", "successful"
        ]

        has_vague_wording = any(word in lower for word in vague_words)

        if "sensationalism_only" in route:
            print("[FEEDBACK] Branch: sensationalism_only", flush=True)
            return {
                "issue_code": FactCheckController.ISSUE_CODES["SENSATIONAL"],
                "issue_type": "Sensational wording",
                "problem": "This sentence uses dramatic or attention-grabbing wording that may reduce credibility.",
                "hint": "Use more neutral and factual language.",
                "better_direction": "Rewrite the sentence in a calm and precise way without exaggeration."
            }

        if time_inconsistent:
            print("[FEEDBACK] Branch: time_inconsistent", flush=True)
            return {
                "issue_code": FactCheckController.ISSUE_CODES["TIME"],
                "issue_type": "Timeline inconsistency",
                "problem": "The sentence may mix future wording with language that suggests the event has already happened.",
                "hint": "Check whether the event is planned, ongoing, or completed.",
                "better_direction": "Rewrite the sentence so the timing is clear and consistent."
            }
        
        future_year_match = re.search(r"\b20\d{2}\b", sentence)
        current_year = datetime.now().year

        if future_year_match:
            year = int(future_year_match.group())
            
            if year > current_year:
                print("[FEEDBACK] Branch: future claim", flush=True)
                return {
                    "issue_code": FactCheckController.ISSUE_CODES["WEAK_SUPPORT"],
                    "issue_type": "Future claim",
                    "problem": "This sentence refers to a future event or policy that cannot be fully verified yet.",
                    "hint": "Check whether this is an official announcement, plan, or speculation.",
                    "better_direction": "Clarify that this is a planned or proposed change and include a source if available."
                }
        
        if "opinion" in route:
            return {
                "issue_code": FactCheckController.ISSUE_CODES["OK"],
                "issue_type": "Opinion statement",
                "problem": "This sentence expresses an opinion or viewpoint rather than a directly verifiable fact.",
                "hint": "Opinions are not fact-checked the same way as factual claims.",
                "better_direction": "Keep it as opinion, or add supporting facts if you want to strengthen the statement."
            }
        
        if "market_data" in route:
            return {
                "issue_code": FactCheckController.ISSUE_CODES["OK"],
                "issue_type": "Market update",
                "problem": "This sentence appears to report time-sensitive market data.",
                "hint": "Market prices can change quickly, so the time and source are important.",
                "better_direction": "Keep the statement factual and include a timestamp or source if available."
            }
        
        if has_vague_wording and general_result and general_result.get("verdict") == "Plausible":
            return {
                "issue_code": FactCheckController.ISSUE_CODES["VAGUE"],
                "issue_type": "Vague claim",
                "problem": "The claim appears plausible, but the wording is too vague.",
                "hint": "Consider making the statement more specific with clearer details or attribution.",
                "better_direction": "Rewrite the sentence to clearly state who is involved, what happened, and what evidence supports it."
            }

        if stats_result and stats_result.get("ok") and stats_result.get("matched"):
            if stats_result.get("result") == "match":
                return {
                    "issue_code": FactCheckController.ISSUE_CODES["OK"],
                    "issue_type": "Verified statistic",
                    "problem": "This number matches trusted official data.",
                    "hint": "You can strengthen the sentence further by citing the source clearly.",
                    "better_direction": "Keep the figure accurate and include the official source if appropriate."
                }
            if stats_result.get("result") == "close":
                return {
                    "issue_code": FactCheckController.ISSUE_CODES["STAT_YEAR"],
                    "issue_type": "Minor statistical difference",
                    "problem": "The number is close to official data but does not match exactly.",
                    "hint": "Check the exact figure, rounding, and reporting year.",
                    "better_direction": "Use the precise official number and cite the source clearly."
                }
            
            if stats_result.get("result") == "mismatch":
                print("[FEEDBACK] Branch: statistical mismatch", flush=True)
                return {
                    "issue_code": FactCheckController.ISSUE_CODES["STAT_MISMATCH"],
                    "issue_type": "Statistical mismatch",
                    "problem": "The number in this sentence may not match trusted official data.",
                    "hint": "Check the figure, year, and source before publishing.",
                    "better_direction": "Use the latest official statistic and clearly cite the source."
                }

            if stats_result.get("year_note"):
                print("[FEEDBACK] Branch: year clarification", flush=True)
                return {
                    "issue_code": FactCheckController.ISSUE_CODES["STAT_YEAR"],
                    "issue_type": "Year clarification needed",
                    "problem": "The statistic may refer to a year that does not match the latest available official data.",
                    "hint": "Clarify the year and make sure the number matches the correct reporting period.",
                    "better_direction": "Rewrite the sentence to clearly state the exact year of the official figure."
                }
            
        if (
            "statistical_check" in route
            and (not stats_result or not stats_result.get("ok"))
            and general_result
            and general_result.get("verdict") == "Plausible"
        ):
            return {
                "issue_code": FactCheckController.ISSUE_CODES["WEAK_SUPPORT"],
                "issue_type": "Plausible but unverified statistic",
                "problem": "The numerical claim appears plausible but is not supported by verified statistical data.",
                "hint": "Consider adding an official source or dataset to support the figure.",
                "better_direction": "Include the source or report that provides the statistic to improve reliability."
            }
            
        if "statistical_check" in route and (not stats_result or not stats_result.get("ok")):
            return {
                "issue_code": FactCheckController.ISSUE_CODES["WEAK_SUPPORT"],
                "issue_type": "Needs statistical source",
                "problem": "This numerical claim could not be verified using trusted official statistics.",
                "hint": "Add the source, reporting period, or official dataset behind the figure.",
                "better_direction": "Rewrite the sentence to include the exact source or report that supports the statistic."
            }

        if google_result and google_result.get("ok") and google_result.get("matched"):
            rating = (google_result.get("rating") or "").lower()

            negative_words = [
                "false", "misleading", "incorrect", "unsupported",
                "disputed", "unproven", "unfounded", "no evidence"
            ]

            caution_words = [
                "missing context", "partly true", "half true",
                "needs context", "out of context", "mixed"
            ]

            if any(word in rating for word in negative_words):
                print("[FEEDBACK] Branch: google fact-check conflict", flush=True)
                return {
                    "issue_code": FactCheckController.ISSUE_CODES["FACTCHECK"],
                    "issue_type": "Possible fact-check conflict",
                    "problem": "This claim may conflict with existing published fact-check findings.",
                    "hint": "Review the claim carefully and compare it with reliable fact-check sources.",
                    "better_direction": "Revise the sentence to reflect verified information or add stronger evidence."
                }

            if any(word in rating for word in caution_words):
                print("[FEEDBACK] Branch: google fact-check caution", flush=True)
                return {
                    "issue_code": FactCheckController.ISSUE_CODES["WEAK_SUPPORT"],
                    "issue_type": "Context may be incomplete",
                    "problem": "This claim may require additional context to avoid being misleading.",
                    "hint": "Consider whether the statement leaves out important background or qualifications.",
                    "better_direction": "Add the missing context or clarify the full circumstances behind the claim."
                }

        is_short = len(sentence.split()) <= 4
        has_named_entity = len(routed.get("entities", [])) > 0
        has_number = FactCheckController.has_number(sentence)
        has_action_word = any(
            word in lower for word in [
                "said", "confirmed", "announced", "reported", "launched",
                "arrested", "died", "won", "approved", "banned", "rose", "fell"
            ]
        )

        if is_short and not has_named_entity and not has_number and not has_action_word:
            print("[FEEDBACK] Branch: incomplete sentence", flush=True)
            return {
                "issue_code": FactCheckController.ISSUE_CODES["FRAGMENT"],
                "issue_type": "Incomplete sentence",
                "problem": "This looks more like a sentence fragment than a complete factual statement.",
                "hint": "Rewrite it as a full sentence so readers can clearly understand the meaning.",
                "better_direction": "State who is involved, what happened, and why it matters."
            }

        strong_words = ["always", "never", "definitely", "undeniably", "completely", "guaranteed"]
        has_strong_wording = any(word in lower for word in strong_words)

        if has_strong_wording:
            if general_result and general_result.get("verdict") in ["Questionable", "Unlikely"]:
                print("[FEEDBACK] Branch: strong wording + weak verdict -> LLM feedback", flush=True)
                return FactCheckController.generate_sentence_feedback_with_llm(sentence, routed)

            print("[FEEDBACK] Branch: strong wording -> rule feedback", flush=True)
            return {
                "issue_code": FactCheckController.ISSUE_CODES["ABSOLUTE"],
                "issue_type": "Overly strong wording",
                "problem": "The sentence uses absolute language that may be difficult to verify.",
                "hint": "Use more careful wording unless there is strong evidence.",
                "better_direction": "Replace absolute words with more precise and balanced language."
            }

        if "authority_source" in route or "reported_speech" in route:
            if general_result and general_result.get("verdict") in ["Questionable", "Unlikely"]:
                print("[FEEDBACK] Branch: authority/reported speech -> LLM feedback", flush=True)
                return FactCheckController.generate_sentence_feedback_with_llm(sentence, routed)

            print("[FEEDBACK] Branch: authority/reported speech -> rule feedback", flush=True)
            return {
                "issue_code": FactCheckController.ISSUE_CODES["AUTHORITY"],
                "issue_type": "Attributed statement",
                "problem": "This sentence is presented as information from an authority or named source.",
                "hint": "Make sure the source is clearly identified and the statement is accurately represented.",
                "better_direction": "Include the organisation or speaker name clearly and add context such as date, document, or event if available."
            }

        if general_result and general_result.get("verdict") in ["Questionable", "Unlikely"]:
            print("[FEEDBACK] Branch: general weak claim -> LLM feedback", flush=True)
            return FactCheckController.generate_sentence_feedback_with_llm(sentence, routed)

        if general_result and general_result.get("verdict") == "Plausible":
            try:
                confidence = float(general_result.get("confidence", 0))
            except Exception:
                confidence = 0

            if confidence < 0.75:
                print("[FEEDBACK] Branch: plausible but low confidence", flush=True)
                return {
                    "issue_code": FactCheckController.ISSUE_CODES["WEAK_SUPPORT"],
                    "issue_type": "Could be clearer",
                    "problem": "The claim appears plausible, but the supporting evidence is not strong enough.",
                    "hint": "Consider adding more specific details or attribution to strengthen the claim.",
                    "better_direction": "Include clearer evidence or a source to improve confidence in the statement."
                }

        print("[FEEDBACK] Branch: default", flush=True)
        return {
            "issue_code": FactCheckController.ISSUE_CODES["OK"],
            "issue_type": "No major issue",
            "problem": "This sentence appears clear and does not show any obvious issues.",
            "hint": "You may still strengthen it by adding a source or supporting detail if needed.",
            "better_direction": "Keep the statement clear and ensure supporting evidence is included where appropriate."
        }
    
    @staticmethod
    def build_display_metadata(routed):
        stats_result = routed.get("statistical_result")
        google_result = routed.get("google_factcheck_result")
        general_result = routed.get("general_result")
        route = routed.get("route", [])

        severity = "neutral"
        tag = "Checked"
        flagged = False

        if routed.get("time_inconsistent"):
            severity = "danger"
            tag = "Time issue"
            flagged = True

        elif stats_result and stats_result.get("ok") and stats_result.get("matched"):
            if stats_result.get("result") == "mismatch":
                severity = "danger"
                tag = "Stat mismatch"
                flagged = True
            elif stats_result.get("result") == "close":
                severity = "warning"
                tag = "Stat close"
                flagged = True
            elif stats_result.get("year_note"):
                severity = "warning"
                tag = "Year caution"
                flagged = True
            elif stats_result.get("result") == "match":
                severity = "good"
                tag = "Verified"

        elif google_result and google_result.get("ok") and google_result.get("matched"):
            rating = (google_result.get("rating") or "").lower()
            false_words = ["false", "misleading", "incorrect", "unsupported", "unfounded", "disputed", "unproven"]
            true_words = ["true", "correct", "accurate", "verified", "confirmed"]

            if any(w in rating for w in false_words):
                severity = "danger"
                tag = "Fact-check flagged"
                flagged = True
            elif any(w in rating for w in true_words):
                severity = "good"
                tag = "Fact-check found"
            else:
                severity = "warning"
                tag = "Fact-check found"
                flagged = True

        elif general_result:
            verdict = general_result.get("verdict")
            if verdict == "Unlikely":
                severity = "danger"
                tag = "Unlikely"
                flagged = True
            elif verdict == "Questionable":
                severity = "warning"
                tag = "Needs review"
                flagged = True
            elif verdict == "Plausible":
                severity = "good"
                tag = "Plausible"

        elif "market_data" in route:
            severity = "neutral"
            tag = "Market"

        elif "authority_source" in route:
            severity = "neutral"
            tag = "Authority"

        elif "opinion" in route:
            severity = "neutral"
            tag = "Opinion"

        return {
            "severity": severity,
            "tag": tag,
            "flagged": flagged
        }