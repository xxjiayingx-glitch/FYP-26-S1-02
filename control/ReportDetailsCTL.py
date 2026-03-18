from entity.ReportedArticle import ReportedArticle

class ReportDetails:
    def list_report_details(self, report_id):
        return ReportedArticle.get_report_details(report_id)
    
