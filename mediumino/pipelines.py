# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import JsonItemExporter
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os.path

class MediuminoPipeline(object):
    def __init__(self):
        self.file = open(os.path.join(os.getcwd(),"dist","medium.json"), 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
        self.generateHtml(spider, "index.html", "index-template.html", spider.medium_detected_language, spider.medium_min_clap)
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def generateHtml(self, spider, nomFichierSortie, nomFichierTemplate, detectedLanguage, medium_min_clap):
        spider.logger.info('Building file %s' % nomFichierSortie )
        
        #initialize `PackageLoader` with the directory to look for HTML templates
        env = Environment(loader=FileSystemLoader( os.path.join(os.getcwd(), "templates")), autoescape=select_autoescape(['html', 'xml']))
        template = env.get_template(nomFichierTemplate)

        #crawled_data = json.load(open(os.path.join(os.getcwd(),"dist","medium.json"), 'r', encoding='utf-8'))
        with open(os.path.join(os.getcwd(),"dist","medium.json"), encoding='utf-8') as json_file:  
            crawled_data = json.load(json_file)

            fichier_sortie = open(os.path.join(os.getcwd(),"dist",nomFichierSortie) , 'w', encoding='utf-8')
            fichier_sortie.write(template.render(posts = crawled_data))
            fichier_sortie.close()
