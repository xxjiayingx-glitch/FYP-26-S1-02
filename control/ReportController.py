from entity.Report import report_article

def report(articleID,userID,reason):

    report_article(articleID,userID,reason)

    print("Article Reported")