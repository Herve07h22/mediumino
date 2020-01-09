from jinja2 import Environment, FileSystemLoader, select_autoescape
import os.path
from datetime import datetime,timedelta
import requests
import json

def get_parameter(key, default_value):
    if key in os.environ:
        return os.environ[key]
    else:
        return default_value

def find_article_by_slug(articles, slug):
    article = [a for a in articles if a["postSlug"]== slug]
    if len(article)>0:
        return article[0]
    else:
        return None

def get_data_from_scraping_hub(apikey, projectId, language):
    scrapingHubData = requests.get("https://storage.scrapinghub.com/items/"+str(projectId), auth=(apikey, ''))
    articles        = [ json.loads(l) for l in scrapingHubData.text.splitlines() ]
    # On sélectionne uniquement les articles du langage 
    articles_filtres = [a for a in articles if a["detectedLanguage"] == language]
    # On les ordonne par clap (important pour retenir le doublon le + à jour)
    articles_filtres.sort(key = lambda x : x['postTotalClapCount'] , reverse=True) 
    # On supprime les doublons
    post_slugs        = list(set([a["postSlug"] for a in articles_filtres]))
    articles_uniques  = [ find_article_by_slug(articles_filtres, slug) for slug in post_slugs]
    return articles_uniques

def generate_html(language, nomFichierSortie, nomFichierTemplate, crawled_data):
    print('Building file %s' % nomFichierSortie )
    
    env = Environment(loader=FileSystemLoader( os.path.join(os.getcwd(), "templates")), autoescape=select_autoescape(['html', 'xml']))
    template = env.get_template(nomFichierTemplate)

    crawled_data.sort(key = lambda x : x['postTotalClapCount'] , reverse=True)
    fichier_sortie = open(os.path.join(os.getcwd(),"dist",nomFichierSortie) , 'w', encoding='utf-8')
    fichier_sortie.write(template.render(posts = crawled_data, language=language , posts_number = len(crawled_data), today=(datetime.now() + timedelta(days=-7)).strftime("%Y-%m-%d")))
    fichier_sortie.close()

def generate_json(crawled_data):
    with open(os.path.join(os.getcwd(),"dist","medium.json"), 'w') as outfile:
        json.dump(crawled_data, outfile)

def generate():
    language    = get_parameter('MEDIUMINO_LANGUAGE', 'fr')
    apikey      = get_parameter('SCRAPING_HUB_API_KEY', '')
    projectId   = get_parameter('SCRAPING_HUB_POJECT_ID', '424132')
    crawled_data= get_data_from_scraping_hub(apikey, projectId, language)
    generate_json(crawled_data)
    if language == 'fr' :
            generate_html(language, "index.html", "index-template.html", crawled_data)
            generate_html(language, "newsletter.rss", "newsletter-template.html", crawled_data)
    if language == 'pt' :
        generate_html(language, "index.html", "index-template.pt.html", crawled_data)


generate()

