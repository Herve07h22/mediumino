# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import JsonItemExporter
from scrapy.exceptions import DropItem
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os.path
from datetime import datetime,timedelta

class MediuminoPipeline(object):
    def __init__(self):
        self.posts_seen = set()
        self.file = open(os.path.join(os.getcwd(),"dist","medium.json"), 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
        if spider.medium_detected_language == 'fr' :
            self.generateHtml(spider, "index.html", "index-template.html")
            self.generateHtml(spider, "newsletter.rss", "newsletter-template.html")
        if spider.medium_detected_language == 'pt' :
            self.generateHtml(spider, "index.html", "index-template.pt.html")
 
    def process_item(self, item, spider):
        if item['postId'] in self.posts_seen:
            raise DropItem("Duplicate item found: %s" % item['postId'])
        else:
            self.posts_seen.add(item['postId'])
            self.exporter.export_item(item)
            return item

    def generateHtml(self, spider, nomFichierSortie, nomFichierTemplate):
        spider.logger.info('Building file %s' % nomFichierSortie )
        
        #initialize `PackageLoader` with the directory to look for HTML templates
        env = Environment(loader=FileSystemLoader( os.path.join(os.getcwd(), "templates")), autoescape=select_autoescape(['html', 'xml']))
        template = env.get_template(nomFichierTemplate)

        #crawled_data = json.load(open(os.path.join(os.getcwd(),"dist","medium.json"), 'r', encoding='utf-8'))
        with open(os.path.join(os.getcwd(),"dist","medium.json"), encoding='utf-8') as json_file:  
            crawled_data = json.load(json_file)
            crawled_data.sort(key = lambda x : x['postTotalClapCount'] , reverse=True)
            fichier_sortie = open(os.path.join(os.getcwd(),"dist",nomFichierSortie) , 'w', encoding='utf-8')
            fichier_sortie.write(template.render(posts = crawled_data, language=spider.medium_detected_language , posts_number = len(crawled_data), today=(datetime.now() + timedelta(days=-7)).strftime("%Y-%m-%d")))
            fichier_sortie.close()
