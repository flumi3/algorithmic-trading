from backtest.backtest import Backtest
from api.binance import Binance
from collections import OrderedDict
from market_data import MarketData
from strategies.moving_average_strategy import MovingAverageStrategy
from uuid import UUID
from backtest.signals import BuySignal, SellSignal
from plotly.graph_objs import Figure


def main() -> None:
    # Create market data
    symbol: str = "BTCEUR"
    interval: str = "1h"
    binance: Binance = Binance()
    market_data: MarketData = MarketData(binance.get_candlestick_data(symbol, interval))
    market_data.add_sma("slow_sma", 30)  # Add indicator

    # Run strategy on market data
    strategy: MovingAverageStrategy = MovingAverageStrategy()
    buy_signals: OrderedDict[UUID, BuySignal] = strategy.calc_buy_signals(market_data.candlestick_data)
    sell_signals: OrderedDict[UUID, SellSignal] = strategy.calc_sell_signals(market_data.candlestick_data, buy_signals)

    # Backtest
    api: str = binance.name
    strategy_name: str = strategy.name
    capital: float = 50000.0
    quantity: float = 1.0
    transaction_fee: float = binance.TRADING_FEE

    backtest: Backtest = Backtest(symbol, api, strategy_name, capital, quantity, transaction_fee, market_data,
                                  buy_signals=buy_signals, sell_signals=sell_signals)
    backtest.run_backtest()

    candlestick_fig: Figure = backtest.create_candlestick_figure()
    capital_fig: Figure = backtest.create_capital_figure()
    backtest.figures_to_html([candlestick_fig, capital_fig])


if __name__ == "__main__":
    main()
