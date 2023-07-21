import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
#自作モジュール
from gmo_api import GmoApi_private


class DataCoolector:
    def __init__(self, api_key: str, secret_key: str, save_dir: str, interval: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.save_dir = save_dir
        self.interval = interval
        self.gmo_api_private = GmoApi_private(api_key, secret_key)

    def collect_data(self):
        # 保存するデータの期間(現在は一日前からのデータを取得)
        str_date = pd.to_datetime(datetime.now().date().strftime('%Y%m%d')) - relativedelta(days = 1)
        end_date = pd.to_datetime(datetime.now().date().strftime('%Y%m%d'))

        # シンボルのリストを取得
        symbols = [item['symbol'] for item in self.gmo_api_private.GmoApi_public.get_ticker()['data']]

        now_date = str_date
        while (now_date <= end_date):
            print(now_date)
            for symbol in symbols:
                klines = self.gmo_api_private.GmoApi_public.get_klines(symbol=symbol, interval=self.interval, date=now_date.strftime('%Y%m%d'))['data']
                save_dir = f'{self.save_dir}{self.interval}/{symbol}/'
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                pd.DataFrame(klines).to_csv(f"{save_dir}{symbol}_{self.interval}_{now_date.strftime('%Y%m%d')}.csv", index=False)
            now_date = now_date + relativedelta(days = 1)

        return