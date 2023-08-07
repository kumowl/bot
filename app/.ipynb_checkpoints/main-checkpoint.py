import os
import json
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from data_collect import DataCollector
from predict import Predictor
from position import Position
from deal import Deal
from logger import Logger  # assuming the logger class is in logger.py file
import time

class MainApp:
    def __init__(self):
        # ディレクトリ設定
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # config.jsonの読み込み
        with open("./config.json", 'r') as f:
            self.config = json.load(f)
        
        # Create Logger
        self.logger = Logger('logs/my_log.csv')

        self.api_key = self.config['GMO_API_KEY']
        self.secret_key = self.config['GMO_API_SECRET']

        self.data_collector = DataCollector(api_key=self.api_key, secret_key=self.secret_key, save_dir=self.config['data_dir'], interval=self.config['interval'])
        self.predictor = Predictor(data_dir=self.config['data_dir'], interval=self.config['interval'], long_theta=self.config['long_theta'], short_theta=self.config['short_theta'], symbols=self.config['symbols'], model=self.config['model'])
        self.position = Position(df=self.predictor.df, api_key=self.api_key, secret_key=self.secret_key, symbols=self.config['symbols'])

        self.scheduler = BlockingScheduler()

    def run(self):
        start_time = time.time()
        self.data_collector.collect_data()

        start_time = time.time()
        self.predictor.load_and_preprocess_data()

        start_time = time.time()
        long_list, short_list = self.predictor.get_predictions_and_results()

        start_time = time.time()
        available_list = self.position.get_available_list()

        start_time = time.time()
        self.position.cancel_orders()

        deal = Deal(df=self.predictor.df, api_key=self.api_key, secret_key=self.secret_key, symbols=self.config['symbols'], long_list=long_list, short_list=short_list, available_list=available_list, limit_leverage=self.config['limit_leverage'])

        start_time = time.time()
        deal.order()

        # Log the result
        df_output = pd.DataFrame({
            'datetime': [datetime.now()],
            'available_list': [available_list],
            'long_list': [long_list],
            'short_list': [short_list]
        })
        self.logger.log_dataframe(df_output)
        
    def start_scheduler(self):
        self.scheduler.add_job(self.run, 'cron', minute='*/5', second='1')
        self.scheduler.start()

if __name__ == "__main__":
    app = MainApp()
    app.start_scheduler()

    # Keep the script running.
    while True:
        time.sleep(1)
