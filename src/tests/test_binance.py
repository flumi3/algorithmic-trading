import sys
from pathlib import Path
from typing import List

from pandas import DataFrame

project_root = Path(__file__).parent.parent
sys.path.insert(1, str(project_root))
from api.binance import Binance

binance: Binance = Binance()


def test_get_candlestick_data():
    candlestick_data = binance.get_candlestick_data(symbol="BTCEUR", interval="1h")
    assert isinstance(candlestick_data, DataFrame)
    col_names: List[str] = ["time", "open", "high", "low", "close", "volume", "date"]
    assert list(candlestick_data.columns) == col_names


def test_get_coherent_candlestick_data():
    candlestick_data = binance.get_candlestick_data(symbol="BTCEUR", interval="1h", limit=2150)
    assert isinstance(candlestick_data, DataFrame)
    assert len(candlestick_data.index) == 2148  # 2148 because we loose 2 rows when concatenating the frames


def test_get_current_price():
    # Check for one symbol
    symbol_price = binance.get_current_price("BTCEUR")
    assert symbol_price
    assert isinstance(symbol_price, float)

    # Check for all symbols
    prices = binance.get_current_price()
    assert prices
    assert isinstance(prices, dict)
    for symbol, price in prices.items():
        assert isinstance(price, float)
