
from asyncio.windows_events import NULL
import yfinance as yf
from flask import Flask, render_template, request, url_for, redirect, session
from flask_session import Session
import plotly.graph_objs as go
import plotly
import json

app = Flask(__name__)
sess = Session()


@app.route("/", methods=['GET','POST'])
def index():
    if request.method == 'POST':
        session['stock_name'] = request.form['stock_search']
        quote = yf.Ticker(session['stock_name'])
        
        if len(session['stock_name']) == 0:
            return render_template('error.html')
        else:
            return redirect(url_for('quote'))
    else:
        return render_template('index.html')
    
    

@app.route("/quote", methods=['GET', 'POST'])
def quote():
    company = session.get('stock_name', None)
    quote = yf.Ticker(str(company))
    team = (quote.info["dayHigh"], quote.info["dayLow"])
    upperCompany = company.upper()
    data = yf.download(tickers=upperCompany, period = '5d', interval = '15m', rounding= True)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,open = data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name = 'market data'))
    fig.update_layout(title = quote.info['longName'] + " (" + upperCompany + ")" + ' | Share Price: $' + str("{:.2f}".format(quote.info["currentPrice"])) + " | Day High, Low: " + "$" + str("{:.2f}".format(quote.info["dayHigh"]))  + ", " + "$" + str("{:.2f}".format(quote.info["dayLow"])), yaxis_title = 'Stock Price (USD)')
    fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
    buttons=list([
    dict(count=15, label='15m', step="minute", stepmode="backward"),
    dict(count=45, label='45m', step="minute", stepmode="backward"),
    dict(count=1, label='1h', step="hour", stepmode="backward"),
    dict(count=6, label='6h', step="hour", stepmode="backward"),
    dict(step="all")
    ])
    )
    )


    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('quote.html',graphJSON=graphJSON)


@app.route("/about")
def about():
    return render_template('about.html')




if __name__ == "__main__":
    #app.run(debug=True)

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)
    app.run(debug=True)