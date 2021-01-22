import flair as fl
import requests
import pandas as pd
import math
import joblib as jl
from StockSentimentAnalyst.getdataprocedures import *
from StockSentimentAnalyst import config


class TweetAnalyzer:

    def analyzetweets(self,ticker,tweetdays,tweetcount):
        #ticker = input("enter the ticker ").strip()
        apiToken= config.tweeter_token
        bearerToken = 'Bearer ' + apiToken
        params = {
            #'query':'(tsla OR tesla or elon musk) (lang:en)',

            'query':f'{ticker} (lang:en)',
            'max_results' : f'{tweetcount}',
            'tweet.fields':'created_at,lang'
        }
        headers={
            'authorization':f'{bearerToken}'
        }

        #DateTime format required by twitter for query
        dtformat = '%Y-%m-%dT%H:%M:%SZ'

        now=datetime.now() #curent date time
        duration = now-timedelta(days=int(tweetdays)) # last x days date for the tweet range
        now=now.strftime(dtformat) # convert into twitter acceptable format

        tweets =pd.DataFrame() # initialize the tweets dataframe

        while True:
            if datetime.strptime(now,dtformat) < duration :
                break
            prev60 = time_travel(now,60) # get last 60min date time
            params['start_time'] = prev60
            params['end_time'] = now
            twt_response = requests.get('https://api.twitter.com/2/tweets/search/recent',
                                        headers=headers,
                                        params=params
                                        )
            if twt_response:
         # check if the returned response has some tweets or not in the meta data
                if twt_response.json()['meta']['result_count'] > 0:
                    for tweet in twt_response.json()['data']:
                        row=tweetData(tweet)
                        tweets=tweets.append(row,ignore_index=True)

            else:
                print("Errored")
                break
            now=prev60
        #clean the text of the tweets
        tweets['text']=tweets['text'].apply(tweetClean)
        probability= []
        sentiments = []
        #load the flair sentimental model from pickle file
        # with open('StockSentimentAnalyst/Flair_Sentimental_Model.pkl','rb') as file:
        #     sentiment_model=jl.load(file)
        sentiment_model = fl.models.TextClassifier.load('en-sentiment')
        for tweet in tweets['text'].to_list():
            sentence=fl.data.Sentence(tweet)
            sentiment_model.predict(sentence)
            probability.append(sentence.labels[0].score) #sco'query':'(tsla OR tesla or elon musk) (lang:en)',ere btw 0-1
            sentiments.append(sentence.labels[0].value) # Postive or Negative
        #
        tweets['probability']=probability
        tweets['sentiment']=sentiments
        positivetweets = tweets[tweets['sentiment'] == 'POSITIVE'].shape[0]
        negativetweets = tweets[tweets['sentiment'] == 'NEGATIVE'].shape[0]
        totaltweets = positivetweets + negativetweets
        positivepercentage = math.ceil(positivetweets / totaltweets * 100)
        negativepercentage = math.floor(negativetweets / totaltweets * 100)


        return tweets,positivetweets,negativetweets,positivepercentage,negativepercentage

