from flask import Flask,request,abort
import ccxt
import time
import os
import setting
import math
import logging
import logging.handlers

app = Flask(__name__)

coincheck = ccxt.coincheck()
coincheck.apiKey = os.environ.get("APIKEY")
coincheck.secret = os.environ.get("SECRET")

@app.route('/')
def index():
    return "paibot is running..."

@app.route('/webhook',methods=['POST'])
def webhook():
    if request.method == 'POST':
        message = request.get_data(as_text=True)
        app.logger.info("webhook message:" + message)

        balance = coincheck.fetchBalance()["info"]
        balance_jpy = math.floor(float(balance["jpy"]))
        balance_btc = round(float(balance["btc"]),8)

        #Nonceを1つ増加させるため1秒停止
        time.sleep(1)

        if "buy" in message:
            order = coincheck.create_market_buy_order('BTC/JPY',balance_jpy)
            app.logger.info("order id: %s %s %s",order['info']['id'] , order['info']['order_type'] , order['info']['amount'])
            return '',200           
        elif "sell" in message:
            order = coincheck.create_market_sell_order('BTC/JPY',balance_btc)
            app.logger.info("order id: %s %s %s",order['info']['id'] , order['info']['order_type'] , order['info']['market_buy_amount'])
            return '',200
        else:
            abort(400)
    else:
        abort(403)

@app.errorhandler(Exception)
def server_error(err):
    app.logger.exception(err)
    return '', 500

if __name__ == '__main__':
    
    #ログ設定
    app.logger.setLevel(logging.DEBUG)
    
    #アプリケーションログ
    handler = logging.handlers.RotatingFileHandler("app.log", maxBytes=100000, backupCount=10)
    handler.setLevel(logging.DEBUG) 
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
    app.logger.addHandler(handler)

    #アクセスログ
    logger = logging.getLogger('werkzeug')
    handler = logging.handlers.RotatingFileHandler('access.log',maxBytes=100000, backupCount=10)
    logger.addHandler(handler)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    
    app.run(host="0.0.0.0",port="80")