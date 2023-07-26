import pandas as pd
import pandas.errors
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sklearn.preprocessing import LabelEncoder
import joblib


class Predictor:
    def __init__(self, data_dir: str, interval: str, long_theta: float, short_theta: float, symbols: list, model: str):
        self.data_dir = data_dir
        self.interval = interval
        self.long_theta = long_theta
        self.short_theta = short_theta
        self.symbols = symbols
        self.df = pd.DataFrame()
        self.model = joblib.load(model)
        
    def load_and_preprocess_data(self):
        use_str_date = pd.to_datetime(datetime.now().date().strftime('%Y%m%d')) - relativedelta(days=1)
        use_end_date = pd.to_datetime(datetime.now().date().strftime('%Y%m%d'))

        for symbol in self.symbols:
            for date in pd.date_range(start=use_str_date, end=use_end_date):
                try:
                    temp_df = pd.read_csv(f'{self.data_dir}{self.interval}/{symbol}/{symbol}_{self.interval}_{date.strftime("%Y%m%d")}.csv')
                    temp_df['symbol'] = symbol
                    self.df = pd.concat([self.df, temp_df], axis=0)
                except (FileNotFoundError, pd.errors.EmptyDataError):
                    print(f'File {self.data_dir}{self.interval}/{symbol}/{symbol}_{self.interval}_{date.strftime("%Y%m%d")}.csv not found or empty. Skipping...')

    
        self.df['openTime'] = pd.to_datetime(self.df['openTime'], unit='ms')
        self.df["datetime_f"] = self.df['openTime']
        self.df["symbol_f"] = self.df['symbol']
        self.df.set_index(['openTime', 'symbol'], inplace=True)

        self.df = self._cal_technical_f(self.df)
        self.df = self._cal_category_f(self.df)
        self.df = self._cal_target(self.df)

        le = LabelEncoder()
        self.df['symbol_f'] = le.fit_transform(self.df['symbol_f'])


    def _cal_technical_f(self, df):
        df = df.copy()
        for i in [5, 20]:
            df[f"{i}sma_d_rate"] = df.groupby("symbol")["close"].transform(lambda x: x / (x.rolling(i).mean()) - 1)
        df["past_1return"] = df.groupby("symbol")["close"].transform(lambda x: x / x.shift(1) - 1)
        df["h_l_by_c"] = (df["high"] - df["low"]) / df["close"]
        df["c_o_by_c"] = (df["close"] - df["open"]) / df["close"]
        return df

    def _cal_category_f(self, df):
        df = df.copy()
        df["month"] = df["datetime_f"].dt.month
        df["day"] = df["datetime_f"].dt.day
        df["hour"] = df["datetime_f"].dt.hour
        df["week"] = df["datetime_f"].dt.dayofweek
        return df

    def _cal_target(self, df):
        df.loc[:, "return"] = df.groupby("symbol")["close"].transform(lambda x: x.shift(-1) / x - 1)
        df.loc[:, "return_rank"] = df.groupby("openTime")["return"].transform(lambda x: x.rank(method="min"))
        return df

    def get_predictions_and_results(self):
        f_list = ["volume", "5sma_d_rate", "20sma_d_rate", "past_1return", "h_l_by_c", "c_o_by_c", "symbol_f", "hour"]
        self.df.loc[:, "predict_value"] = self.model.predict(self.df[f_list]).copy()
        self.df["predict_rank"] = self.df.groupby("openTime")["predict_value"].transform(lambda x: x.rank(method="min"))

        now_df = list(self.df.groupby(level='openTime'))[-1][1]
        long_list = now_df.loc[self.df["predict_rank"] > int(len(self.symbols) * self.long_theta)].index.get_level_values('symbol').to_list()
        short_list = now_df.loc[self.df["predict_rank"] <= int(len(self.symbols) * self.short_theta)].index.get_level_values('symbol').to_list()

        return long_list, short_list