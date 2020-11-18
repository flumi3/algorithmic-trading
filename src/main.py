import os

from backtest import Backtest
from api.binance import Binance
from typing import List
from market_data import MarketData
from strategies.moving_average_strategy import MovingAvergageStrategy
from transaction import Transaction
from util import datestr_to_timestamp

def main() -> None:
    binance: Binance = Binance()
    backtest: Backtest = Backtest()
    strategy: MovingAvergageStrategy = MovingAvergageStrategy()

    root_dir: str = os.path.dirname(os.path.abspath("Algorithmic-Trading"))
    symbol: str = "BTCEUR"
    interval: str = "1h"
    
    # Create market data
    market_data: MarketData = MarketData(binance.get_candlestick_data(symbol, interval))

    # Add indicator for moving average strategy
    market_data.add_SMA("slow_sma", 30)

    # Run backtest strategy on market data
    buy_signals: List[Transaction] = strategy.calc_buy_signals(market_data.candlestick_data)
    sell_signals: List[Transaction] = strategy.calc_sell_signals(market_data.candlestick_data, 1.02, buy_signals)
    
    plot_title: str = root_dir + "/" + symbol
    backtest.plot_candlestick_chart(market_data, plot_title, buy_signals, sell_signals)


if __name__ == "__main__":
    main()
