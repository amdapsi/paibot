from flask import Flask,request,abort
import ccxt
import time
import os
import setting
import math
import logging
import logging.handlers
import json

app = Flask(__name__)



@app.route('/')
def index():
    return "paibot is running..."

@app.route('/webhook',methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.get_json()
        app.logger.info("webhook message:" + json.dumps(data))

        if data["exchange"] == "coincheck":

            coincheck = ccxt.coincheck()
            coincheck.apiKey = os.environ.get("COINCHECK_APIKEY")
            coincheck.secret = os.environ.get("COINCHECK_SECRET")
            
            balance = coincheck.fetchBalance()["info"]
            balance_jpy = math.floor(float(balance["jpy"]))
            balance_btc = round(float(balance["btc"]),8)
            
            #Nonceを1つ増加させるため1秒停止
            time.sleep(1)
            
            if data["order"] == "buy":
                btc_price = coincheck.fetchTicker("BTC/JPY")["info"]["last"]
                amount = math.floor(btc_price * data["lot"]) 
                order = coincheck.create_market_buy_order('BTC/JPY',amount)
                app.logger.info("order id: %s %s %s",order['info']['id'] , order['info']['order_type'] , order['info']['market_buy_amount'])
                return '',200           
            elif data["order"] == "sell":
                amount = data["lot"] if data["lot"] < balance_btc else round(balance_btc,8)
                order = coincheck.create_market_sell_order('BTC/JPY',amount) 
                app.logger.info("order id: %s %s %s",order['info']['id'] , order['info']['order_type'] , order['info']['amount'])
                return '',200
            else:
                abort(400)
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