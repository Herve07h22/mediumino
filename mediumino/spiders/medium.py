# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import os

def get_parameter(key, default_value):
    if key in os.environ:
        return os.environ[key]
    else:
        return default_value

class MediumSpider(scrapy.Spider):
    name = 'medium'
    allowed_domains = ['medium.com']

    users_api_url = 'https://medium.com/_/api/users/{}/profile/stream?page=20&limit=100'
    responses_api_url = 'https://medium.com/_/api/posts/{}/responses'
    followers_api_url = 'https://medium.com/_/api/users/{}/following'
    
    # A adapter pour utiliserles variables d'environnement
    #start_urls = [ 
    #    users_api_url.format('be7f6e99fc1c'),
    #    users_api_url.format('aa757ffbadd'), 
    #    users_api_url.format('c5cee4d3c8ab'),    
    #    users_api_url.format('d092df4c7445'), 
    #    users_api_url.format('3cbc6d00320d'),
    #    ]

    def start_requests(self):
        self.medium_detected_language = get_parameter('MEDIUMINO_LANGUAGE', 'fr')
        self.medium_min_clap = int(get_parameter('MEDIUMINO_MIN_CLAP', '100'))
        self.medium_start_user = get_parameter('MEDIUMINO_USER_ID', 'be7f6e99fc1c')
        self.medium_start_user_page = 0
        start_urls_resquests = [  scrapy.Request(self.users_api_url.format( self.medium_start_user)) ]
        return start_urls_resquests
    
    # pour la version Brazil
    # start_urls = [ users_api_url.format('e011446d0731') ]
    # medium_detected_language = 'pt'
    # medium_min_clap = 100

    def parse(self, response):
        r = json.loads(response.text[16:])
        # who is the author ?
        userId = r['payload']['user']['userId']
        userName = r['payload']['user']['username']
        publishedName = r['payload']['user']['name']
        authorWritesSelectedLanguage = False
        # crawling the posts matching the conditions
        if 'Post' in r['payload']['references'] :
            posts = r['payload']['references']['Post']
            for key in posts.keys():
                if posts[key]['detectedLanguage'] == self.medium_detected_language :
                    authorWritesSelectedLanguage = True
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
                        # parse responses to find new authors
                        # yield scrapy.Request(url = self.responses_api_url.format(postId), callback=self.parse_responses)
        if authorWritesSelectedLanguage:
            self.medium_start_user_page = 0
            yield scrapy.Request(url = self.followers_api_url.format(userId), callback=self.parse_followers)
        # if userId == self.medium_start_user:
        #yield scrapy.Request(url = self.followers_api_url.format(userId), callback=self.parse_followers)

    def parse_followers(self, response):
        # parse all the followers
        r = json.loads(response.text[16:])
        for follower in r['payload']['value']:
            #self.logger.info('Crawling follower %s' % follower['name'] )
            yield scrapy.Request(url = self.users_api_url.format(follower['userId']), callback=self.parse)
        if 'next' in r['payload']['paging'] and self.medium_start_user_page < 10 :  
            yield scrapy.Request(url = "https://medium.com" + r['payload']['paging']['path'] + "?page=" + str(self.medium_start_user_page) , callback=self.parse_followers)
            self.medium_start_user_page += 1
            

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
