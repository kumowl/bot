import os
import json
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from data_collect import DataCollector
from predict import Predictor
from position import Position
from deal import Deal
import time

class MainApp:
    def __init__(self):
        # ディレクトリ設定
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # config.jsonの読み込み
        with open("./config.json", 'r') as f:
            self.config = json.load(f)
        
        # 環境変数の読み込み
        #load_dotenv()

        #self.api_key = os.environ.get('GMO_API_KEY')
        #self.secret_key = os.environ.get('GMO_API_SECRET')

        self.api_key = self.config['GMO_API_KEY']
        self.secret_key = self.config['GMO_API_SECRET']


        self.data_collector = DataCollector(api_key=self.api_key, secret_key=self.secret_key, save_dir=self.config['data_dir'], interval=self.config['interval'])
        self.predictor = Predictor(data_dir=self.config['data_dir'], interval=self.config['interval'], long_theta=self.config['long_theta'], short_theta=self.config['short_theta'], symbols=self.config['symbols'], model=self.config['model'])
        self.position = Position(df=self.predictor.df, api_key=self.api_key, secret_key=self.secret_key, symbols=self.config['symbols'])
        #self.deal = Deal(df=self.predictor.df, api_key=self.api_key, secret_key=self.secret_key, symbols=self.config['symbols'], long_list=self.long_list, short_list=self.short_list, available_list=self.position.available_list, limit_leverage=self.config['limit_leverage'])

        self.scheduler = BlockingScheduler()

    def run(self):
        start_time = time.time()
        print("処理を始めます：" + str(start_time))
        self.data_collector.collect_data()
        print("data_collector.collect_data took %s seconds" % (time.time() - start_time))

        start_time = time.time()
        self.predictor.load_and_preprocess_data()
        print("predictor.load_and_preprocess_data took %s seconds" % (time.time() - start_time))

        start_time = time.time()
        long_list, short_list = self.predictor.get_predictions_and_results()
        print("predictor.get_predictions_and_results took %s seconds" % (time.time() - start_time))

        print('long_list---------------')
        print(long_list)
        print('short_list---------------')
        print(short_list)

        start_time = time.time()
        available_list = self.position.get_available_list()
        print('available_list---------------')
        print(available_list)
        print("position.get_available_list took %s seconds" % (time.time() - start_time))

        start_time = time.time()
        self.position.cancel_orders()
        print("position.cancel_orders took %s seconds" % (time.time() - start_time))

        deal = Deal(df=self.predictor.df, api_key=self.api_key, secret_key=self.secret_key, symbols=self.config['symbols'], long_list=long_list, short_list=short_list, available_list=available_list, limit_leverage=self.config['limit_leverage'])

        start_time = time.time()
        deal.order()
        print("deal.order took %s seconds" % (time.time() - start_time))
        
        
    def start_scheduler(self):
        self.scheduler.add_job(self.run, 'cron', minute='*/5', second='1')
        self.scheduler.start()

if __name__ == "__main__":
    app = MainApp()
    app.start_scheduler()

    # Keep the script running.
    while True:
        time.sleep(1)