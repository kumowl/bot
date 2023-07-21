import os
import json
from dotenv import load_dotenv
# from data_collect import collect_data
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

class MainApp:
    def __init__(self) -> None:
        # ディレクトリ設定
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.data_save_dir = "../data/"

        # setting.jsonの読み込み
        with open("./setting.json", 'r') as f:
            self.config = json.load(f)
        
        # 環境変数の読み込み
        load_dotenv()
        self.api_key = os.environ.get('GMO_API_KEY')
        self.secret_key = os.environ.get('GMO_API_SECRET')


        # Create an instance of scheduler
        self.scheduler = BlockingScheduler()

        # Add job function to the scheduler
        self.scheduler.add_job(self.job, 'interval', seconds=10)

    def job_test(self):
        # Get current time
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")

        # Create an empty file with current time as name
        with open(f"{self.data_save_dir}/{current_time}.txt", 'w') as f:
            pass

    def start(self):
        # Start the scheduler
        self.scheduler.start()

if __name__ == "__main__":
    app = MainApp()
    app.start()