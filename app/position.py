import pandas as pd
from datetime import datetime
#自作モジュール
from gmo_api import GmoApi_private
from gmo_api import GmoApi_public


class position:
    def __init__(self, df: pd.DataFrame, api_key: str, secret_key: str, symbols: list):
        self.df = df
        self.api_key = api_key
        self.secret_key = secret_key
        self.gmo_api_private = GmoApi_private(api_key, secret_key)
        self.available_list = []
        self.symbols = symbols

    def cancel_orders(self):
        self.gmo_api_private.cancel_all_orders(symbols=self.symbols)

    def get_available_list(self):
        position_df = pd.DataFrame(self.gmo_api_private.get_balance()['data'])
        position_df[['amount', 'available', 'conversionRate']] = position_df[['amount', 'available', 'conversionRate']].astype(float)

        self.available_list = position_df.loc[position_df['available']*position_df['conversionRate'] > 100]['symbol'].tolist()
        self.available_list.remove('JPY') if 'JPY' in self.available_list else self.available_list

        return self.available_list