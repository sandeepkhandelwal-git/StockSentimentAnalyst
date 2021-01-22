import pandas as pd
from datetime import datetime,timedelta
import plotly.graph_objects as go
from plotly.offline import plot
from plotly.subplots import make_subplots

class GetPlot:

    def getplot(self,tweets,yfdf):

        chartframe = pd.DataFrame()
        chartframe['Datetime'] = yfdf['Datetime'].astype(str)
        chartframe['Close'] = yfdf['Close']
        chartframe['Open'] = yfdf['Open']
        chartframe['High'] = yfdf['High']
        chartframe['Low'] = yfdf['Low']
        chartframe['Positive'] = "" #creating Positive Column for positive sentiment count
        chartframe['Negative'] = "" #creating Positive Column for negative sentiment count

        for id, date in enumerate(chartframe['Datetime']):
            date_obj = datetime.strptime(date[0:19], '%Y-%m-%d %H:%M:%S')
            nexthour = date_obj + timedelta(hours=1)
            poscount = 0
            negcount = 0
            for idx, tdate in enumerate(tweets['created_date']):
                tdate_obj = datetime.strptime(tdate, '%Y-%m-%dT%H:%M:%S.%fZ')
                if date_obj <= tdate_obj < nexthour:
                    if tweets['sentiment'][idx] == 'POSITIVE':
                        poscount += 1
                    else:
                        negcount += 1
            chartframe['Positive'][id] = poscount
            chartframe['Negative'][id] = negcount

        #print(chartframe)
    #--------------------------------------------------------------------
    # Create the Plot using the chartframe dataframe
    #--------------------------------------------------------------------

    # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        #fig.add_trace(go.Scatter(x=chartframe['Datetime'], y=chartframe['Price'], name='Price Action', marker={'color': 'blue'},mode='lines'))
        fig.add_trace(go.Candlestick(x=chartframe['Datetime'],open=chartframe['Open'],high=chartframe['High'],low=chartframe['Low'],
                                     close=chartframe['Close']),secondary_y=True)
        fig.add_trace(go.Bar(name='Positive', x=chartframe['Datetime'], y=chartframe['Positive'], marker={'color': '#AAB399'}))
        fig.add_trace(go.Bar(name='Negative', x=chartframe['Datetime'], y=chartframe['Negative'], marker={'color': '#FAA685'}))
        fig.layout.yaxis2.showgrid = False
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(barmode='stack',
                          width=700,
                          height=400,
                          margin=dict(
                              l=25,
                              r=25,
                              b=50,
                              t=50,
                              pad=1,
                          ),
                          autosize=False,
                          )
        plt_div = plot(fig, output_type='div', include_plotlyjs=False,
                       show_link=False, link_text='')

        return plt_div