from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
import os
from django.conf import settings as djangoSettings
import math
import pandas as pd
from datetime import datetime
import pathlib
import json
import wordcloud
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from get_all_tickers.get_tickers import get_biggest_n_tickers
from StockSentimentAnalyst.forms import StockSentimentAnalystForm
from StockSentimentAnalyst.externalapicalls import *
from StockSentimentAnalyst.tweetanalyzer import TweetAnalyzer
from StockSentimentAnalyst.getplot import GetPlot
from StockAnalysis import settings

class StockSentimentAnalystIndex(TemplateView):
    template_name = 'StockSentimentAnalyst/index.html'
    tickerLoadAtStart = 'DJIA'
    tweetCountAtStart = 15
    tweetDaysAtStart  = 5
    #initialize the externalapicalls
    yfapicall = YahooFinanceApiCall()
    tweetanalyzer = TweetAnalyzer()
    getplotdiv = GetPlot()

 #----------------------------------------------------------------------------
    # get Function definition
# ----------------------------------------------------------------------------
    def get(self,request):

        form=StockSentimentAnalystForm()

        # get News from NewApi
        newapicall = NewApiCall()
        newsDataResponse = newapicall.getlatestheadlines()
        #convert returned newdata dataframe to json format to use in template
        newsDataJson = newsDataResponse[:6].reset_index().to_json(orient='records')
        newsData = []
        newsData=json.loads(newsDataJson)

        # get the tweet details for the ticker
        tweets,positivetweets,negativetweets,positivepercentage,negativepercentage= \
            self.tweetanalyzer.analyzetweets('dowjones',self.tweetDaysAtStart,self.tweetCountAtStart)

        # extract wordlcoud out of the tweets
        # wordCloudFilePath = os.path.join(pathlib.Path(__file__).parent.absolute(),
        #                                  "static/assets/images/wordcloud/wordcloud.png")
        wordCloudFilePath = os.path.join(settings.BASE_DIR,
                                         "static/StockSentimentAnalyst/assets/images/wordcloud/wordcloud.png")
        allWords = ' '.join(twts for twts in tweets['text'])
        wordCloud = wordcloud.WordCloud(width=400,height=300,random_state=21,max_font_size=119).generate(allWords)
        plt.imshow(wordCloud)
        plt.axis('off')
        plt.savefig(wordCloudFilePath)

        # extract data for first load

        startDate = datetime.datetime.strptime(tweets['created_date'].min(), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
        endDate = datetime.datetime.strptime(tweets['created_date'].max(), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
        yfdf = self.yfapicall.getyfinancedata(self.tickerLoadAtStart,startDate=startDate,endDate=endDate)
        plt_div = self.getplotdiv.getplot(tweets,yfdf)
        if not plt_div:
            plt_div = "Data Not Present for the Selected Ticker"
        context={

           'form' : form,
           'plt_div' : plt_div,
            'ticker' :self.tickerLoadAtStart,
            'positivetweets':positivetweets,
            'negativetweets' : negativetweets,
            'positivepercentage': positivepercentage,
            'negativepercentage':negativepercentage,
            'newsdata': newsData

        }


        return render(request,self.template_name,context=context)

#----------------------------------------------------------------------------
    # post Function definition
# ----------------------------------------------------------------------------

    def post(self,request):
        form = StockSentimentAnalystForm(request.POST or None)
        error =''

        if form.is_valid():
            ticker=form.cleaned_data['tickers']
            tweet_counts=form.cleaned_data['tweet_count']
            tweet_days=form.cleaned_data['tweet_day']

            if ticker=="0" or tweet_days=="0" or tweet_counts=="0":
                error='Y'
                errorDescription='Please select values for Stock Ticker & Tweet Count & Days'
                form=StockSentimentAnalystForm()
                context = {
                    'form':form,
                            'error':error,
                            'errorDescription':errorDescription,
                }
            else:

                # get News from NewApi
                newapicall = NewApiCall()
                newsDataResponse = newapicall.getlatestnewsonticker(ticker)
                # convert returned newdata dataframe to json format to use in template
                newsDataJson = newsDataResponse[:6].reset_index().to_json(orient='records')
                newsData = []
                newsData = json.loads(newsDataJson)
                print(newsData)
                #Tweet Data
                tweets, positivetweets, negativetweets, positivepercentage, negativepercentage = \
                    self.tweetanalyzer.analyzetweets(ticker, tweet_days,tweet_counts)
                # extract wordlcoud out of the tweets
                #wordCloudFilePath = os.path.join(pathlib.Path(__file__).parent.absolute(),
                #                                 "static/assets/images/wordcloud/wordcloud.png")
                wordCloudFilePath = os.path.join(settings.BASE_DIR,
                                                 "static/StockSentimentAnalyst/assets/images/wordcloud/wordcloud.png")
                allWords = ' '.join(twts for twts in tweets['text'])
                wordCloud = wordcloud.WordCloud(width=400, height=300, random_state=21, max_font_size=119).generate(
                    allWords)
                plt.imshow(wordCloud)
                plt.axis('off')
                plt.savefig(wordCloudFilePath)
                print(ticker)
                #Get Ticker Financial Details from Yahoo
                startDate = datetime.datetime.strptime(tweets['created_date'].min(), '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
                    '%Y-%m-%d')
                endDate = datetime.datetime.strptime(tweets['created_date'].max(), '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
                    '%Y-%m-%d')
                yfdf = self.yfapicall.getyfinancedata(ticker,startDate=startDate,endDate=endDate)

                plt_div = self.getplotdiv.getplot(tweets,yfdf)
                if not plt_div:
                    plt_div = "Data Not Present for the Selected Ticker"


                context = {

                    'form': form,
                    'plt_div': plt_div,
                    'ticker': ticker,
                    'positivetweets': positivetweets,
                    'negativetweets': negativetweets,
                    'positivepercentage': positivepercentage,
                    'negativepercentage': negativepercentage,
                    'newsdata': newsData,
                    'error':error,
                    'errorDescription':''


                }
        else:
            plt_div = form.cleaned_data['tickers']
            form = StockSentimentAnalystForm()

            context={'form':form, 'plt_div':plt_div}
        return render(request, self.template_name, context=context)