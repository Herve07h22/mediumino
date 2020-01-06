# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import os
import random



class MediumSpider(scrapy.Spider):
    name = 'medium'
    allowed_domains = ['medium.com']

    users_api_url = 'https://medium.com/_/api/users/{}/profile/stream?page=20&limit=100'
    #followers_api_url = 'https://medium.com/_/api/users/{}/following'
    followers_api_url = 'https://medium.com/_/api/users/{}/profile/stream?source=followers'

    banned_users = ['kgasbarra8']
    
    def start_requests(self):
        self.medium_detected_language = self.get_parameter('MEDIUMINO_LANGUAGE', 'fr')
        self.medium_min_clap = int(self.get_parameter('MEDIUMINO_MIN_CLAP', '100'))
        self.medium_start_user = self.get_parameter('MEDIUMINO_USER_ID', 'be7f6e99fc1c')
        self.medium_start_user_page = 0
        print("medium_detected_language:", self.medium_detected_language)
        print("medium_min_clap:", self.medium_min_clap)
        print("medium_start_user:", self.medium_start_user)

        return [ scrapy.Request(self.users_api_url.format( self.medium_start_user)) ]
    
    def get_parameter(self,key, default_value):
        if key in os.environ:
            return os.environ[key]
        else:
            return self.settings.get(key) or default_value

    def parse(self, response):
        r = json.loads(response.text[16:])
        # who is the author ?
        userId = r['payload']['user']['userId']
        userName = r['payload']['user']['username']
        publishedName = r['payload']['user']['name']
        authorWritesSelectedLanguage = False
        self.logger.info('Parsing author : %s', userName)
        # check if not banned
        banned = userName in self.banned_users
        # crawling the posts matching the conditions
        if 'Post' in r['payload']['references'] and not banned:
            posts = r['payload']['references']['Post']
            # On shuffle un peu les keys
            #print("keys :", str(posts.keys()))
            #shuffled_keys = self.shuffle_array([ *posts.keys() ])
            #print("shuffled_keys :", shuffled_keys)
            for key in sorted(posts.keys(), key=lambda k: random.random()):
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
                        authorWritesSelectedLanguage = True
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
                        
        if authorWritesSelectedLanguage:
            #self.logger.info('Parsing followers of author : %s', userName)
            self.medium_start_user_page = 0
            yield scrapy.Request(url = self.followers_api_url.format(userId), callback=self.parse_followers)

    def parse_followers(self, response):
        # parse all the followers
        r = json.loads(response.text[16:])
        if 'Social' in r['payload']['references']:
            # On shuffle un peu les followers
            #followers = r['payload']['references']['Social'].copy()
            #random.shuffle(followers)

            for follower in sorted(r['payload']['references']['Social'], key=lambda k: random.random()):
                #self.logger.info('Parsing followers TargetUserId = %s', follower)
                yield scrapy.Request(url = self.users_api_url.format(follower), callback=self.parse)
        
        if 'next' in r['payload']['paging'] and self.medium_start_user_page < 20 :
            next = r['payload']['paging']['next']
            if 'to' in next :
                #self.logger.info('Getting url %s', r['payload']['paging']['path'] + "?page=" + str(next['page']) + "&to=" + next['to'] + "&source=followers")
                yield scrapy.Request(url = r['payload']['paging']['path'] + "?page=" + str(next['page']) + "&to=" + next['to'] + "&source=followers" , callback=self.parse_followers)
                self.medium_start_user_page += 1            


