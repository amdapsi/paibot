from flask import Flask,request,abort
import ccxt
import time
import os
import setting

app = Flask(__name__)
coincheck = ccxt.coincheck()
coincheck.apiKey = os.environ.get("COINCHECK_APIKEY")
coincheck.secret = os.environ.get("COINCHECK_SECRET")

@app.route('/webhook',methods=['POST'])
def webhook():
    if request.method == 'POST':
        message = request.get_data(as_text=True)
        balance = coincheck.fetchBalance()["info"]
        #1秒に2回以上認証が必要なリクエストが発行できないため1秒停止
        time.sleep(1)
        balance_jpy = round(float(balance["jpy"]))
        balance_btc = round(float(balance["btc"]),8)
        if message in "buy":
            coincheck.create_market_buy_order('BTC/JPY',balance_jpy)
            return '',200           
        elif message in "sell":
            coincheck.create_market_buy_order('BTC/JPY',balance_btc)
            return '',200
        else:
            abort(400)
    else:
        abort(403)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="80")