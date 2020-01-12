from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure, show
from bokeh.palettes import Set1 as palette
from bokeh.embed import components
import pandas as pd
import simplejson as json

import requests
import itertools

def _convert_date(s, fmt='%Y-%m-%d'):
    output = pd.to_datetime(s, format=fmt)
    return output

def _url(stock, columns):
    if type(columns) is not list:
        columns = [columns]
    columns.append('date')
    api_key = 'api_key=T1uisS-t1xu7ASeQHMzx'
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?'
    keys = 'qopts.columns=' + ','.join(columns)
    ticker = 'ticker=%s' %(stock.upper())

    output = url + keys + '&' + ticker + '&' + api_key

    return output

def query_data(stock, columns):
    url = _url(stock, columns)

    try:
        j = requests.get(url)
        output = pd.DataFrame(json.loads(j.content)['datatable']['data'], columns=columns)
    except:
        return 'File not found'
    output['date'] = output['date'].apply(_convert_date)
    output.set_index('date', inplace=True)

    return output

def plot_data(data, stock, height=400, width=1.618*400, tools='pan,box_zoom,wheel_zoom,reset,crosshair,hover,save', **kwargs):
    end = pd.to_datetime('2018-1-1')
    start = end - pd.DateOffset(years=1)

    temp = data.loc[end:start]

    x = temp.index
    colors = itertools.cycle(palette[8])

    p = figure(tools=tools, title=stock.upper(), x_axis_label='Date', y_axis_label='Value', x_axis_type='datetime')
    for key, color in zip(temp.columns, colors):
        p.line(x, temp[key], color=color, legend=key)
    p.legend.location = 'bottom_left'
    script, div = components(p)

    return script, div

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('stock_form.html')

    else:
    	# Determine stock and columns to display
        stock = request.form['stock']
        if not stock:
            stock = 'AAPL'
        # columns = [request.form['columns1'], request.form['columns2'], request.form['columns3'], request.form['columns4']]
        columns = request.form.getlist('columns')
        if not columns:
            columns = ['open']

        # Query Quandl API for data
        data = query_data(stock, columns)

        # Produce plot
        script, div = plot_data(data, stock)
    	# Embed plot into HTML via Flask Render
        return render_template("stock_plot.html", script=script, div=div)
        # return render_template('about', stock=stock, columns=columns)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
