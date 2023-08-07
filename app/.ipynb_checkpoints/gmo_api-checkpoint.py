import json
import hmac
import hashlib
import time
import requests
from datetime import datetime
import math

class GmoApi_private:
    endpoint = 'https://api.coin.z.com/private'

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        #publicのクラスの呼び出し
        self.GmoApi_public = GmoApi_public()

    #APIのヘッダーを取得
    def get_headers(self, method, path, reqBody=None):
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        if reqBody:
            text = timestamp + method + path + json.dumps(reqBody)
        else:
            text = timestamp + method + path
        sign = hmac.new(bytes(self.api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            "API-KEY": self.api_key,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }
        return headers
    
    #余力情報を取得
    def get_margin(self):
        method = 'GET'
        path = '/v1/account/margin'
        headers = self.get_headers(method, path)
        response = requests.get(self.endpoint + path, headers=headers)
        return response.json()
    
    #資産残高を取得
    def get_balance(self):
        method = 'GET'
        path = '/v1/account/assets'
        headers = self.get_headers(method, path)
        response = requests.get(self.endpoint + path, headers=headers)
        return response.json()
    
    #取引高情報を取得
    def get_tradingVolume(self):
        method = 'GET'
        path = '/v1/account/tradingVolume'
        headers = self.get_headers(method, path)
        response = requests.get(self.endpoint + path, headers=headers)
        return response.json()
    
    #注文情報取得
    def get_orders(self, orderId:str): #カンマ区切りで最大10件まで指定可能
        method = 'GET'
        path = '/v1/orders'
        parameters = {"orderId":orderId}
        headers = self.get_headers(method, path)
        response = requests.get(self.endpoint + path, headers=headers, params= parameters)
        return response.json()
    
    #有効注文一覧
    def get_activeOrders(self, symbol:str, page:int = None, count:int = None):
        method = 'GET'
        path = '/v1/activeOrders'
        parameters = {
            "symbol": symbol,
            "page": page,
            "count": count
        }
        headers = self.get_headers(method, path)
        response = requests.get(self.endpoint + path, headers=headers, params= parameters)
        return response.json()


    #約定情報取得
    def get_latestExecutions(self, symbol:str, page:int = None, count:int = None):
        method = 'GET'
        path = '/v1/latestExecutions'
        parameters = {
            "symbol": symbol,
            "page": page,
            "count": count
        }
        headers = self.get_headers(method, path)
        response = requests.get(self.endpoint + path, headers=headers, params= parameters)
        return response.json()

    #注文
    def post_order2(self, symbol:str, side:str, executionType:str, size:str, price:str=None, timeInForce:str=None, losscutPrice:str=None, cancelBefore:bool=None):
        method = 'POST'
        path = '/v1/order'
        reqBody = {
            "symbol": symbol,
            "side": side,
            "executionType": executionType,
            "size": size,
            "price":price,
            "timeInForce":timeInForce,
            "losscutPrice":losscutPrice,
            "cancelBefore":cancelBefore
        }

        headers = self.get_headers(method, path, reqBody)
        response = requests.post(self.endpoint + path, headers=headers, data = json.dumps(reqBody))
        return response.json()

    def post_order(self, symbol:str, side:str, executionType:str, size:str, price:str=None, timeInForce:str=None, losscutPrice:str=None, cancelBefore:bool=None):
        size = float(size)
        method = 'POST'
        path = '/v1/order'

        #symbolの最低注文数量を取得
        rules = self.GmoApi_public.get_rules()['data']
        minOrderSize = float(next(item['minOrderSize'] for item in rules if item['symbol'] == symbol))
        #実際に注文できる数量を計算
        #小数点以下の桁数をカウントする関数
        def count_decimal_places(number):
            num_str = str(number)
            if '.' in num_str:
                return len(num_str) - num_str.index('.') - 1
            else:
                return 0
        # sizeをminOrderSizeで除算し、結果を下に丸める
        rounded_size = math.floor(size / minOrderSize)
        # 結果を再びminOrderSizeで乗算して近似値を得る
        decimal_places = count_decimal_places(minOrderSize)
        approx_size = round(rounded_size * minOrderSize, decimal_places)
        # if minOrderSize is integer, make approx_size integer
        if minOrderSize.is_integer():
            approx_size = int(approx_size)

        size = str(approx_size)
        
        reqBody = {
            "symbol": symbol,
            "side": side,
            "executionType": executionType,
            "size": size,
            "price":price,
            "timeInForce":timeInForce,
            "losscutPrice":losscutPrice,
            "cancelBefore":cancelBefore
        }

        headers = self.get_headers(method, path, reqBody)
        response = requests.post(self.endpoint + path, headers=headers, data = json.dumps(reqBody))
        return response.json()
    
    def post_order_by_JPY(self, symbol:str, side:str, executionType:str, jpy_size:str, price:str=None, timeInForce:str=None, losscutPrice:str=None, cancelBefore:bool=None):
        jpy_size = float(jpy_size)
        #対象銘柄の価格を取得
        last_price = float(self.GmoApi_public.get_ticker(symbol)['data'][0]['last'])
        #指定した日本円に値する注文サイズを計算
        size = jpy_size/last_price
        #symbolの最低注文数量を取得
        rules = self.GmoApi_public.get_rules()['data']
        minOrderSize = float(next(item['minOrderSize'] for item in rules if item['symbol'] == symbol))
        #実際に注文できる数量を計算
        #小数点以下の桁数をカウントする関数
        def count_decimal_places(number):
            num_str = str(number)
            if '.' in num_str:
                return len(num_str) - num_str.index('.') - 1
            else:
                return 0
        # sizeをminOrderSizeで除算し、結果を下に丸める
        rounded_size = math.floor(size / minOrderSize)
        # 結果を再びminOrderSizeで乗算して近似値を得る
        decimal_places = count_decimal_places(minOrderSize)
        approx_size = round(rounded_size * minOrderSize, decimal_places)
        # if minOrderSize is integer, make approx_size integer
        if minOrderSize.is_integer():
            approx_size = int(approx_size)
        #注文を行う
        response = self.post_order(symbol, side, executionType, str(approx_size), price, timeInForce, losscutPrice, cancelBefore)
        return response


    
        #注文の一括キャンセル
    def cancel_all_orders(self, symbols:str, side:str=None, settleType:str=None, desc:bool=None):
        method = 'POST'
        path = '/v1/cancelBulkOrder'
        reqBody = {
            'symbols': symbols,
            'side': side,
            'settleType': settleType,
            'desc': desc
        }

        headers = self.get_headers(method, path, reqBody)
        response = requests.post(self.endpoint + path, headers=headers, data = json.dumps(reqBody))
        return response.json()



#publicAPI
class GmoApi_public:
    endpoint = 'https://api.coin.z.com/public'

    #ticker取得
    def get_ticker(self, symbol:str=None):
        path = '/v1/ticker'
        params = {
            'symbol':symbol
        }
        response = requests.get(self.endpoint + path, params=params)
        return response.json()

    #取引ルールを取得
    def get_rules(self):
        path = '/v1/symbols'
        response = requests.get(self.endpoint + path)
        return response.json()

    #kline情報を取得
    def get_klines(self, symbol, interval, date):
        path = '/v1/klines'
        params = {
            'symbol':symbol,
            'interval':interval,
            'date':date
        }
        response = requests.get(self.endpoint + path, params = params)
        return response.json()
