from apscheduler.schedulers.background import BackgroundScheduler
import time

class MainApp:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def say_hello(self):
        print("おはようございます")

    def start_scheduler(self):
        # 'cron' scheduler, execute at every hour, every 5 minutes, and 1 second
        self.scheduler.add_job(self.say_hello, 'cron', minute='*/1', second='1')
        self.scheduler.start()

if __name__ == "__main__":
    app = MainApp()
    app.start_scheduler()

    # Keep the script running.
    while True:
        time.sleep(1)