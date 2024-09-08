from backtesting import Backtest, Strategy
from backtesting.test import SMA, GOOG
import numpy as np
import pandas as pd #引入pandas讀取股價歷史資料CSV檔
import argparse

class RightHandSide(Strategy):
    n = 5
    def init(self):
        print(self.closed_trades)
        close = self.data.Close
        self.sma = self.I(SMA, close, self.n)
        self.sma_delta = np.diff(self.sma)
        print(np.diff(self.sma))

    def next(self):
        if self.sma_delta > 0:
            if self.position.size <= 0:
                self.buy()
            if self.position and self.position.is_short:
                self.position.close()   
        elif self.sma_delta < 0:
            if self.position.size >= 0:
                self.sell()
            if self.position and self.position.is_long:
                self.position.close()
            


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="hihi")
    parser.add_argument("--stock", type=str, default=2330, help="whick stock")
    parser.add_argument("--long_short", type=str, default="mix", help="long only=long short only=short")
    parser.add_argument("--initial_cash", type=int, default=100000, help="initial cash")
    parser.add_argument("--commision", type=int, default=0.00018, help="commsion")
    parser.add_argument("--show_plot", type=bool, default=False, help="commsion")
    args = parser.parse_args()
    stock = args.stock

    df = pd.read_csv(f"./data/{stock}.csv", index_col=1)
    df.index = pd.to_datetime(df.index)
    df = df.interpolate()
    df.long_short = args.long_short
    bt = Backtest(df, RightHandSide,
                cash=args.initial_cash, commission=args.commision,
                exclusive_orders=True)

    output = bt.run()
    print(output)
    if args.show_plot:
        bt.plot()