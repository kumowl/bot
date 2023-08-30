import os
import datetime
import csv
import pandas as pd
from gmo_api import GmoApi_private
from pathlib import Path
import time

class Logger:
    def __init__(self, api_key, secret_key, symbols):
        self.gmo_api_private = GmoApi_private(api_key, secret_key)
        self.symbols = symbols

    def _mk_dir(self, dir_path):
        if isinstance(dir_path, str):
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        else:
            for i in dir_path:
                Path(i).mkdir(parents=True, exist_ok=True)

    def log_error(self, dir_path, message):
        self._mk_dir(dir_path)

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        with open(f'{dir_path}/error_log.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, message])

    def log_deal(self, dir_path, df):
        self._mk_dir(dir_path)

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d")

        df.to_csv(f'{dir_path}/{timestamp}_deal_log.csv', mode='a', index=False)
    
    def log_executions(self, dir_path):
        self._mk_dir(dir_path)

        df = pd.DataFrame()
        for symbol in self.symbols:
            response = self.gmo_api_private.get_latestExecutions(symbol=symbol)
            print(response)
            data_list = response['data'].get('list')
            
            # 'list'キーが取得できる場合のみ処理を実行
            if data_list is not None:
                df = pd.concat([df, pd.DataFrame(data_list)], axis=0)
            time.sleep(1)

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d")

        df.to_csv(f'{dir_path}/{timestamp}_execution_long.csv', index=False)



