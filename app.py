
from asyncio.windows_events import NULL
import yfinance as yf
from flask import Flask, render_template, request, url_for, redirect, session
from flask_session import Session
import plotly.graph_objs as go
import plotly
import json
import requests

IP = "127.0.0.1"
PORT = 8081
SERVICE_URL = "http://%s:%d" % (IP, PORT)

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

    upperCompany = company.upper()

    #Microservice interaction
    
    response_store = requests.post(SERVICE_URL + "/store_data", json={
    "image_name": "TSLA",
    "image_path": "https://www.carshowroom.com.au/media/21484061/2020-tesla-roadster-01.jpg"
    })
    response_store_json = response_store.json()
    response_store_success = response_store_json["success"]

    if response_store_success:
        print("Successfully added a new image to the image service!")
    else:
        print("Problem storing a new image to the image service! error message is: \n    \"" + response_store_json["error_message"] + "\"")
    


    # GET an image path from the image service
    response_get = requests.get(SERVICE_URL + "/get_data", json={
        "image_name": upperCompany,
    })
    response_get_json = response_get.json()
    fetched_image_path = response_get_json["image_path"]
    print("fetched image path:", fetched_image_path)

    
    print("\n-----------------------------------------")
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
    return render_template('quote.html',graphJSON=graphJSON, value = fetched_image_path)


@app.route("/about")
def about():
    return render_template('about.html')




if __name__ == "__main__":
    #app.run(debug=True)

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)
    #app.run(debug=True)
    app.run()