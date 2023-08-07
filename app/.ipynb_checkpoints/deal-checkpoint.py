import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
#自作モジュール
from gmo_api import GmoApi_private
from gmo_api import GmoApi_public


class Deal:
    def __init__(self, df: pd.DataFrame, api_key: str, secret_key: str, symbols: list, long_list: list, short_list: list, available_list: list, limit_leverage: int):
        self.api_key = api_key
        self.secret_key = secret_key
        self.gmo_api_private = GmoApi_private(api_key, secret_key)
        self.rule_df = pd.DataFrame(self.gmo_api_private.GmoApi_public.get_rules()['data']) 
        self.df = df
        self.symbols = symbols
        self.long_list = long_list
        self.short_list = short_list
        self.available_list = available_list
        self.limit_leverage = limit_leverage

    def order(self):
        #注文を行う関数
        def round_to_tick_size(number, tick_size):
            if tick_size == 1:
                return round(number)
            else:
                return round(number / tick_size) * tick_size
            
        def order_by_symbol(self, symbol, side, lot):
            last_price = self.df[self.df.index.get_level_values('symbol') == symbol]['close'].tail(1).values[0]
            tick_size = float(self.rule_df[self.rule_df['symbol'] == symbol]['tickSize'].values[0])

            limit_price = None  # 初期化

            if side == 'SELL':
                limit_price = round_to_tick_size(last_price + self.limit_leverage * tick_size, tick_size)
            elif side == 'BUY':
                limit_price = round_to_tick_size(last_price - self.limit_leverage * tick_size, tick_size)

            print(limit_price)

            # 初期化後、limit_price が None のままである場合、エラーメッセージを表示または適切な値を設定することも可能です。
            if limit_price is None:
                print("Error: limit_price is not set. Please check the 'side' value.")
                return

            self.gmo_api_private.post_order_by_JPY(symbol, side, 'LIMIT', str(lot), price=str(limit_price))

        # ロングポジションの注文
        for symbol in self.long_list:
            if ~(symbol in self.available_list):
                print('buy' + symbol)
                order_by_symbol(self, symbol=symbol, side='BUY', lot=1000)

        # ショートポジションの注文
        for symbol in self.short_list:
            if symbol in self.available_list:
                print('sell' + symbol)
                order_by_symbol(self, symbol, side='SELL', lot=1000)