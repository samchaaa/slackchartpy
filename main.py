import requests
import time
import os
import json

import pandas as pd
from datetime import datetime
import pytz

# import matplotlib.pyplot as plt
import mplfinance as mpl

import slack_sdk as slack

SLACK_TOKEN=os.environ['SLACK_TOKEN']
SLACK_CHANNEL=os.environ['SLACK_CHANNEL']
client = slack.WebClient(token=SLACK_TOKEN)

import flask

# yahoo
style = {'base_mpl_style': 'fast',
         'marketcolors'  : {'candle': {'up': '#579FEC', 'down': '#E28E60'},
                            'edge'  : {'up': '#579FEC', 'down': '#E28E60'},
                            'wick'  : {'up': '#579FEC', 'down': '#E28E60'},
                            'ohlc'  : {'up': '#579FEC', 'down': '#E28E60'},
                            'volume': {'up': '#579FEC', 'down': '#E28E60'},
                            'vcedge': {'up': '#579FEC', 'down': '#E28E60'},
         'vcdopcod'      : True,
         'alpha'         : 0.9},
         'mavcolors'     : None,
         'facecolor'     : '#fafafa',
         'gridcolor'     : '#d0d0d0',
         'gridstyle'     : '-',
         'y_on_right'    : False,
         'rc'            : {'axes.labelcolor': '#101010',
                            'axes.edgecolor' : 'f0f0f0',
                            'axes.grid.axis' : 'y',
                            'ytick.color'    : '#101010',
                            'xtick.color'    : '#101010',
                            'figure.titlesize': 'x-large',
                            'figure.titleweight':'semibold',
                           },
         'base_mpf_style': 'yahoo'}

app = flask.Flask(__name__)
@app.route('/', methods=['GET'])
def home():

    code = flask.request.args['code']

    # req data
    
    # start, end = int(time.time()), int(time.time() - 60 * 1440 * 1) # -1d
    start = int(datetime(au_last.year, au_last.month, au_last.day, 10, 0, tzinfo=pytz.timezone('Australia/Melbourne')).timestamp())
    end = int(datetime.now(tz=pytz.timezone('Australia/Melbourne')).timestamp())
    
    url = f"https://au.advfn.com/common/javascript/tradingview/advfn/history?symbol=ASX%5E{code}&resolution=5&v=1&from={start}&to={end}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, headers=headers)
    d = json.loads(r.content)
    d = pd.DataFrame(d)
    d['t'] = pd.to_datetime(d['t'], unit='s')
    d = d.set_index('t')
    d = d.rename(columns={
        'o': 'Open',
        'h': 'High',
        'l': 'Low',
        'c': 'Close',
        'v': 'Volume',
    })
    d.index = d.index.tz_localize('UTC').tz_convert('Australia/Sydney')
    d = d.sort_index()

    # make chart
    mpl.plot(
        d,
        type="candle",
        style=style,
        savefig='chart.png',
        xrotation=30,
        fontscale=0.8,
        volume=True,
        ylabel=code,
        ylabel_lower='',
        scale_padding={
            'left': 0.5,
            'top': 0.5,
            'bottom': 0.75,
            'right': 0.25
        },
        vlines=dict(
            vlines=[_ for _ in d.index if _.time().hour == 15 and _.time().minute == 55],
            alpha=0.5, colors='grey', linestyle='dashed'
        ),
    )

    img = open('chart.png'.format(code), 'rb').read()

    # post to slack
    r2 = client.files_upload(
        channels=SLACK_CHANNEL,
        filename=code,
        content=img
    )

    return r2

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
