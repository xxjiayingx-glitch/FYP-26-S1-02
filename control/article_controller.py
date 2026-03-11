from entity.article_entity import get_articles, search_articles

def view_articles():
    return get_articles()

def search_article(keyword):
    return search_articles(keyword)