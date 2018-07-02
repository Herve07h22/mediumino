# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json

class MediumSpider(scrapy.Spider):
    name = 'medium'
    allowed_domains = ['medium.com']

    users_api_url = 'https://medium.com/_/api/users/{}/profile/stream?page=20&limit=100'
    responses_api_url = 'https://medium.com/_/api/posts/{}/responses'
    
    # pour la version France
    start_urls = [ 
        users_api_url.format('aa757ffbadd'), 
        users_api_url.format('c5cee4d3c8ab'),  
        users_api_url.format('be7f6e99fc1c'),  
        users_api_url.format('6b4c12cab9b4'), 
        users_api_url.format('d092df4c7445'), 
        users_api_url.format('3cbc6d00320d'),
        ]

    medium_detected_language = 'fr'
    medium_min_clap = 30
    
    # pour la version Brazil
    # start_urls = [ users_api_url.format('e011446d0731') ]
    # start_urls = [ ]
    # medium_detected_language = 'pt'
    # medium_min_clap = 100
    
    # https://medium.com/_/api/users/be7f6e99fc1c/profile/stream?limit=50 (moi)
    # https://medium.com/_/api/posts/bac96a1d4928/responses
    # https://medium.com/_/api/users/6b4c12cab9b4/profile/stream  (thomaass)
    #  https://medium.com/_/api/users/c5cee4d3c8ab/profile/stream (autre clé entrée)
    # https://medium.com/_/api/users/{}/profile/stream?page=20&limit=100
    
    def parse(self, response):
        r = json.loads(response.text[16:])
        #analyse de l'auteur
        userId = r['payload']['user']['userId']
        userName = r['payload']['user']['username']
        publishedName = r['payload']['user']['name']
        #analyse des posts (seulement les siens)
        if 'Post' in r['payload']['references'] :
            posts = r['payload']['references']['Post']
            for key in posts.keys():
                if posts[key]['detectedLanguage'] == self.medium_detected_language :
                    postCreatorId = posts[key]['creatorId']
                    postId = posts[key]['id']
                    postTitle = posts[key]['title']
                    postSlug = posts[key]['uniqueSlug']
                    postTotalClapCount = int(posts[key]['virtuals']['totalClapCount'])
                    postPreviewImage = posts[key]['virtuals']['previewImage']['imageId']
                    postFirstPublishedAt = datetime.date(datetime.fromtimestamp(posts[key]['firstPublishedAt']/1000))
                    postType = posts[key]['type']
                    if postTotalClapCount > self.medium_min_clap and userId == postCreatorId and postType == 'Post':
                        yield {
                            'name' : publishedName,
                            'userName' : userName,
                            'publishedName' : publishedName,
                            'userId' : userId,
                            'postId' : postId, 
                            'postTitle' : postTitle, 
                            'postSlug' : postSlug,
                            'postTotalClapCount' : postTotalClapCount, 
                            'postPreviewImage' : postPreviewImage ,
                            'postFirstPublishedAt' : str(postFirstPublishedAt),
                            'year' : postFirstPublishedAt.year,
                            'detectedLanguage' : self.medium_detected_language,
                        }
                    # parse responses to find links
                    # yield scrapy.Request(url = self.responses_api_url.format(postId), callback=self.parse_responses)
                    
    def parse_responses(self, response):
        r = json.loads(response.text[16:])
        for user in list(self.findAllKey('creatorId',r)):
            yield scrapy.Request(url = self.users_api_url.format(user), callback=self.parse)
        
    def findAllKey(self, key, dictionary):
        
        if isinstance(dictionary, list):
            for d in dictionary:
                for result in self.findAllKey(key, d):
                    yield result
        
        if isinstance(dictionary, dict):
            for k, v in dictionary.items():
                if k == key:
                    yield v
                elif isinstance(v, dict):
                    for result in self.findAllKey(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self.findAllKey(key, d):
                            yield result
