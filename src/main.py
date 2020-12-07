import os
import logger  # Don't delete. Executes the log config

from backtest.backtest import Backtest
from api.binance import Binance
from typing import Dict
from market_data import MarketData
from strategies.moving_average_strategy import MovingAverageStrategy
from uuid import UUID
from backtest.signals import BuySignal, SellSignal
from datetime import datetime


def main() -> None:
    # Create market data
    symbol: str = "BTCEUR"
    interval: str = "1h"
    binance: Binance = Binance()
    market_data: MarketData = MarketData(binance.get_candlestick_data(symbol, interval))
    market_data.add_sma("slow_sma", 30)  # Add indicator

    # Run strategy on market data
    strategy: MovingAverageStrategy = MovingAverageStrategy()
    buy_signals: Dict[UUID, BuySignal] = strategy.calc_buy_signals(market_data.candlestick_data)
    sell_signals: Dict[UUID, SellSignal] = strategy.calc_sell_signals(market_data.candlestick_data, buy_signals)

    # Backtest
    api: str = binance.name
    strategy_name: str = strategy.name
    capital: float = 50000.0
    quantity: float = 1.0
    transaction_fee: float = binance.TRADING_FEE
    start_date: datetime = datetime.now()  # TODO: set real date
    end_date: datetime = datetime.now()  # TODO: set real date

    root_dir: str = os.path.dirname(os.path.abspath("Algorithmic-Trading"))
    plot_title: str = root_dir + "/" + symbol

    backtest: Backtest = Backtest(symbol, api, strategy_name, capital, quantity, transaction_fee, start_date, end_date,
                                  market_data, buy_signals=buy_signals, sell_signals=sell_signals)
    backtest.run_backtest()
    backtest.plot_candlestick_chart(plot_title)
    backtest.plot_capital_chart()


if __name__ == "__main__":
    main()
