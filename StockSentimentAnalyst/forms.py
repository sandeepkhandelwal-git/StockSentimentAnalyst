from django import forms
from get_all_tickers.get_tickers import get_biggest_n_tickers

#set the default values for the index page
tweet_counts = [
        (0 ,'Tweet Counts'),
        (10,'10 tweets per hour'),
        (25,'25 tweets per hour'),
        (50,'50 tweets per hour'),
        (75,'75 tweets per hour'),
        (100,'100 tweets per hour')
                    ]

tweet_days= [
        (0 ,'Tweet Days'),
        (1 ,'last 1 day'),
        (2 ,'last 2 day'),
        (3 ,'last 3 day'),
        (4 ,'last 4 day'),
        (5 ,'last 5 day'),
        (6 ,'last 6 day'),
        (7 ,'last week')
                ]

#setting value of first n tickers and extracting stock tickers
n=100
n_tickers = sorted(get_biggest_n_tickers(n,sectors=None))
# use comprehensive list to create the list of tuples
tickers_choice = [(ticker,ticker) for ticker in n_tickers]
tickers_choice.insert(0,('0','Select Stocks...'))

#django form
class StockSentimentAnalystForm(forms.Form):
    tickers = forms.ChoiceField(choices=tickers_choice,label='')
    tweet_count = forms.ChoiceField(label='',choices=tweet_counts,help_text='Tweet Counts')
    tweet_day= forms.ChoiceField(label='',choices=tweet_days,help_text='Tweet Days')
    tickers.widget.attrs.update({'class':'custom-select'})
    tweet_count.widget.attrs.update({'class': 'custom-select'})
    tweet_day.widget.attrs.update({'class': 'custom-select'})
