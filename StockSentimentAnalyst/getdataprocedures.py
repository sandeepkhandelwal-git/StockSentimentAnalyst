import re
from datetime import datetime,timedelta

#DateTime format required by twitter for query
dtformat = '%Y-%m-%dT%H:%M:%SZ'

def tweetData(tweet):
    data={
        'id':tweet['id'],
        'created_date':tweet["created_at"],
        'text':tweet['text'],

    }
    return  data

def tweetClean(tweet):
    whitespace = re.compile(r"\s+")
    web_address = re.compile(r"(?i)http(s):\/\/[a-zA-Z0-9.~_\-\/]+")
    user = re.compile(r"(?i)@[a-z0-9_]+")
    mention = re.compile(r"@[A-Za-z0-9]")
    hash = re.compile(r"#")
    retweet=re.compile(r"RT[\s]")

    tweet = whitespace.sub(' ',tweet)
    tweet = web_address.sub(' ',tweet)
    tweet = user.sub(' ',tweet)
    tweet = hash.sub(' ',tweet)
    tweet = retweet.sub(' ',tweet)
    tweet = mention.sub(' ',tweet)

    return tweet

def time_travel(now,mins):
    now=datetime.strptime(now, dtformat)
    back_in_time = now-timedelta(minutes=mins)
    return back_in_time.strftime(dtformat)

def newsData(news):
    # extract teh date from the datetime string
    match = re.search(r'\d{4}-\d{2}-\d{2}',news['publishedAt'])
    publishDate=datetime.strptime(match.group(),'%Y-%m-%d').strftime("%b %d %Y")
    data={
        'source':news['source']['name'],
        'author':news['author'],
        'title': news['title'],
        'newsUrl':news['url'],
        'newsImage':news['urlToImage'],
        'publishedAt':publishDate
    }
    return data