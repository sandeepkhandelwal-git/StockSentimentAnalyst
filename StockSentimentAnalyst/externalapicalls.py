import yfinance as yf
import requests
import pandas as pd
import datetime
from plotly.offline import plot
import plotly.graph_objects as go
from StockSentimentAnalyst.getdataprocedures import newsData
from StockSentimentAnalyst import config


class YahooFinanceApiCall:

    def getyfinancedata(self,ticker,*arg,**kwargs):
        #ticker = ticker
        startdate = kwargs.get('startDate',None)
        enddate =   kwargs.get('endDate',None)

        yftickerdata = yf.Ticker(ticker)
        yfdf = pd.DataFrame()
        yfdf = yftickerdata.history(
                start=startdate,
                end=enddate,
                prepost=True,
                actions=False,
                interval='60m'
                )
        #yfdf=yftickerdata.history(period="1mo")
        yfdf.reset_index(inplace=True)
        print(yfdf)
        x_data = yfdf['Datetime']
        y_data = yfdf['Close']

     #===========================================================================
        # create Go graphs
     # ===========================================================================
        data=go.Scatter(x=x_data,y=y_data)
        layout = go.Layout(
            plot_bgcolor="lightsteelblue",
            xaxis = dict(
            title = "Hourly Time Frame ",
            linecolor="#BCCCDC",  # Sets color of X-axis line
            showgrid=False  # Removes X-axis grid lines
            ),
            yaxis= dict(
            title = "Price",
            linecolor="#BCCCDC",  # Sets color of Y-axis line
            showgrid=True  # Removes Y-axis grid lines
            ),
            width=700,
            height=400,
            margin=dict(
                        l=25,
                        r=25,
                        b=50,
                        t=50,
                        pad= 1  ,
                    ),
            autosize=False,

        )

        fig = go.Figure(data=data,layout=layout)

        plt_div = plot(fig,output_type='div',include_plotlyjs=False,
                                show_link=False,link_text='')
        return yfdf

class NewApiCall:
    apiKey = config.newsapi_key
    newsApitTickerUrl = 'http://newsapi.org/v2/everything'
    newsApiHeadlinesUrl ='https://newsapi.org/v2/top-headlines'

    def getlatestnewsonticker(self,ticker):

        fromDate = datetime.datetime.now().strftime("%Y-%m-%d")
        params ={
            'q':f'{ticker}',
            'from': fromDate,
            'language':'en',
            'sortBy':'publishedAt',
            'apikey':f'{self.apiKey}',
        }
        newsApiResponse = requests.get(self.newsApitTickerUrl,params=params)
        newsdatadf=pd.DataFrame()
        if newsApiResponse:
            for news in newsApiResponse.json()['articles']:
                row = newsData(news)
                if row['newsImage']:
                    newsdatadf= newsdatadf.append(row,ignore_index=True)


        return newsdatadf


    def getlatestheadlines(self):

        params = {
            'category':'business',
            'country':'us',
            'language': 'en',
            'sortBy': 'publishedAt',
            'apikey': f'{self.apiKey}',
        }
        newsApiResponse = requests.get(self.newsApiHeadlinesUrl, params=params)
        newsdatadf = pd.DataFrame()
        if newsApiResponse:
            for news in newsApiResponse.json()['articles']:
                row = newsData(news)
                if row['newsImage']:
                    newsdatadf = newsdatadf.append(row, ignore_index=True)

        return newsdatadf

