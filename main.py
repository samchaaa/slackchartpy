import requests
import time
import os
import json

import pandas as pd
from datetime import datetime

# import matplotlib.pyplot as plt
import mplfinance as mpl

import slack_sdk as slack

SLACK_TOKEN=os.environ['SLACK_TOKEN']
client = slack.WebClient(token=SLACK_TOKEN)

from flask import Flask

app = Flask(__name__)
@app.route('/', methods=['GET'])
def home():

    code = flask.request.args['code']

    # req data
    start, end = int(time.time()), int(time.time() - 60 * 1440) # -1d
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
        style="binance",
        savefig='{}.png'.format(code),
        xrotation=30,
        fontscale=0.8,
        volume=True,
        ylabel=code,
        ylabel_lower='',
    )

    img = open('chart.png'.format(code), 'rb').read()

    # post to slack
    r2 = client.files_upload(
        channels="#asdf",
        filename='chart.png',
        content=img
    )

    return r2

if __name__ == '__main__':
    app.run(host='', port=8080, debug=True)
