from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG
from talib import abstract
import numpy as np
import pandas as pd #引入pandas讀取股價歷史資料CSV檔



def I_bypass(data): # bypass data in Strategy
    return data

class KDCross(Strategy): 
    lower_bound = 20  
    upper_bound = 80  

    def init(self):
        self.k = self.I(I_bypass, self.data.slowk) #K 
        self.d = self.I(I_bypass, self.data.slowd) #D

    def next(self):
        if crossover(self.k, self.d) and self.k<self.lower_bound and self.d<self.lower_bound and not self.position: #long position
            self.buy() 
        elif crossover(self.d, self.k) and self.k>self.upper_bound and self.d>self.upper_bound: 
            if self.position and self.position.is_long:
                self.position.close()

class SmaCross(Strategy):
    n1 = 5
    n2 = 20
    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)
        self.sma_delta = np.diff(self.sma1)
        print(np.diff(self.sma1))

    def next(self):
        # print(self.sma1[-1])
        # print(self.data.Close[-1])
        # print(self.sma1.diff())
        if self.sma_delta > 0:
            self.buy()
            if self.position and self.position.is_short:
                self.position.close()
        elif self.sma_delta < 0:
            self.sell()
            if self.position and self.position.is_long:
                self.position.close()

class Test(Strategy):
    n1 = 5
    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma_delta = np.diff(self.sma1)
        print(np.diff(self.sma1))

    def next(self):
        if self.sma_delta > 0:
            self.buy()
            if self.position and self.position.is_short:
                self.position.close()
        elif self.sma_delta < 0:
            # self.sell()
            if self.position and self.position.is_long:
                self.position.close()



#calculate KD signal with talib
df_tmp = GOOG
print(GOOG)
df_tmp.rename(columns = {'High':'high', 'Low':'low','Close':'close'}, inplace = True) #rename for talib
kd = abstract.STOCH(df_tmp)
kd.index=df_tmp.index
fnl_df = df_tmp.join(kd).dropna() #merge two data frame
fnl_df.rename(columns = {'high':'High', 'low':'Low','close':'Close'}, inplace = True) #rename column name for backtest

stock = "2454" #設定要測試的股票標的名稱

df = pd.read_csv(f"./data/{stock}.csv", index_col=0) #pandas讀取資料，並將第1欄作為索引欄
df = df.interpolate() #CSV檔案中若有缺漏，會使用內插法自動補值，不一定需要的功能
df.index = pd.to_datetime(df.index) #將索引欄資料轉換成pandas的時間格式，backtesting才有辦法排序
bt = Backtest(df, Test,
              cash=100000, commission=0.00018,
              exclusive_orders=True)

output = bt.run()
print(output)
bt.plot()