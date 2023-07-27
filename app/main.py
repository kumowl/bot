import os
import json
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from data_collect import DataCollector
from predict import Predictor
from position import Position
from deal import Deal

class MainApp:
    def __init__(self):
        # ディレクトリ設定
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # config.jsonの読み込み
        with open("./config.json", 'r') as f:
            self.config = json.load(f)
        
        # 環境変数の読み込み
        load_dotenv()

        self.api_key = os.environ.get('GMO_API_KEY')
        self.secret_key = os.environ.get('GMO_API_SECRET')


        self.data_collector = DataCollector(api_key=self.api_key, secret_key=self.secret_key, save_dir=self.config['data_dir'], interval=self.config['interval'])
        self.predictor = Predictor(data_dir=self.config['data_dir'], interval=self.config['interval'], long_theta=self.config['long_theta'], short_theta=self.config['short_theta'], symbols=self.config['symbols'], model=self.config['model'])
        self.position = Position(df=self.predictor.df, api_key=self.api_key, secret_key=self.secret_key, symbols=self.config['symbols'])
        self.deal = Deal(df=self.predictor.df, api_key=self.api_key, secret_key=self.secret_key, symbols=self.config['symbols'], long_list=self.predictor.long_list, short_list=self.predictor.short_list, available_list=self.position.available_list, limit_leverage=self.config['limit_leverage'])

        self.scheduler = BlockingScheduler()

        
    def run(self):
        self.data_collector.collect_data()

        self.predictor.load_and_preprocess_data()
        long_list, short_list = self.predictor.get_predictions_and_results()

        available_list = self.position.get_available_list()
        self.position.cancel_orders()

        self.deal.order()
        
        
    def start_scheduler(self):
        self.scheduler.add_job(self.run, 'interval', minutes=5)
        self.scheduler.start()

if __name__ == "__main__":
    app = MainApp()
    app.start_scheduler()