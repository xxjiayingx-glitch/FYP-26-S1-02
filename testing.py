from entity.TrustedStatistics import TrustedStatistic
from control.FactCheckCTL import FactCheckController

stat = TrustedStatistic()
result = stat.get_stat_by_metric("singapore_inflation_rate", "Singapore", 2024)

# print(FactCheckController.lookup_statistical_evidence("Singapore's inflation rate rose to 4.8% last year."))
# print(FactCheckController.lookup_statistical_evidence("Singapore's inflation rate rose to 7.8% last year."))

# print(result)

# print(FactCheckController.lookup_newsapi_evidence("Apple announced a new iPhone yesterday."))
print(FactCheckController.lookup_google_fact_check("COVID vaccines cause infertility."))
# print(FactCheckController.lookup_google_fact_check("COVID vaccines cause infertility."))