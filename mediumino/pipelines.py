# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import JsonItemExporter
import json
from jinja2 import Environment, PackageLoader

class JsonPipeline(object):
    def __init__(self):
        self.file = open("medium.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class MediuminoPipeline(object):

    def close_spider(self, spider):
        self.generateHtml(spider, "index.html", "index-template.html", spider.medium_detected_language, spider.medium_min_clap)
    
    def process_item(self, item, spider):
        return item

    def generateHtml(self, spider, nomFichierSortie, nomFichierTemplate, detectedLanguage, medium_min_clap):
        spider.logger.info('Building file %s' % nomFichierSortie )
        
        #initialize `PackageLoader` with the directory to look for HTML templates
        env = Environment(loader=PackageLoader('templates') )
        template = env.get_template(nomFichierTemplate)
        crawled_data = json.loads(open("medium.json", 'r'))

        fichier_sortie = open(nomFichierSortie, 'w')
        fichier_sortie.write(template.render(crawled_data))
        fichier_sortie.close()
