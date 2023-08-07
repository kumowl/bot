import os
import datetime
import csv
import pandas as pd

class Logger:
    def __init__(self, log_file):
        self.log_file = log_file

        # Create log directory if not exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Initialize CSV file with headers if it does not exist
        if not os.path.isfile(log_file):
            with open(log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "message"])

    def log(self, message):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, message])

    def log_dataframe(self, df):
        df.to_csv(self.log_file, mode='a', index=False)