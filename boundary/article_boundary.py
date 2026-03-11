from control.article_controller import view_articles, search_article

def display_articles():

    articles = view_articles()

    for a in articles:
        print(a["articleID"], a["articleTitle"])


def search_articles():

    keyword = input("Keyword: ")

    results = search_article(keyword)

    for r in results:
        print(r["articleTitle"])