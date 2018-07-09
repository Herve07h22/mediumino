# mediumino
A selection of most applaused posts published on Medium.com, written in the language of your choice.
See [Mediumino.fr](https://mediumino.fr) for the French version , and [Mediumino Brazil](https://mediumino.fr/Brazil). 

## Features
* Scrapy crawler engine
* Custom language and minimum applause level
* Single Page Application generation with jinja2
* Designed to be host on netlify

## Installation

* Simply import the repo https://github.com/Herve07h22/mediumino in a new one.
* Create a [netlify](https://www.netlify.com/) account.
* In Netlify, click "new site from git"
* select the git repo you made.
* Add 3 new build environment variables 

| variable           | value 
|--------------------|-----------
| MEDIUMINO_LANGUAGE | fr for French, pt for Portuguese, other keys can be eaysily found  
| MEDIUMINO_MIN_CLAP | 100 (try higher values to test)
| MEDIUMINO_USER_ID  | Your medium ID. Example : be7f6e99fc1c

* Build the site and test

## Custom theme

The theme templates are in `/templates` :
* index-template.html for the Single Page Application that displays the curated posts **TAKE CARE OF USING YOUR OWN GOOGLE ANALYTICS IDs**
* newsletter-template.html for building `newsletter.rss` containing the most recent posts (written in the last 7 days). I use it to send a weekly digest with MailChimp. **TAKE CARE OF USING YOUR OWN MAILCHIMP IDs** 

The templates can use this data structure :

``` bash
Posts = [
    {
        "name": "Full name of the writer", 
        "userName": "URL-compatible name", 
        "userId": "12 alphanum ID", 
        "postId": "12 alphanum ID", 
        "postTitle": "Post title", 
        "postSlug": "post url", 
        "postTotalClapCount": number, 
        "postPreviewImage": "post url",
        "postFirstPublishedAt": "YYYY-MM-DD", 
        "year": YYYY, 
        "detectedLanguage": "pt"
    }, 
]
```
To build the post URL, you have to user the userName and the postSlug :
``` bash
href="{{ "https://medium.com/@" + post.userName + "/" + post.postSlug}}"
```

To build the image URL from the Medium.com CDN :
``` bash
href = "https://cdn-images-1.medium.com/max/200/{{post.postPreviewImage}}"
```
