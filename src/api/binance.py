import requests
import json
import logging
import pandas as pd

from util import BinanceAPIException
from typing import List, Dict, Union
from pandas import DataFrame
from logging import Logger
from requests.models import Response
from json.decoder import JSONDecodeError

logger: Logger = logging.getLogger("__main__")

# Symbols
BITCOIN_EURO: str = "BTCEUR"


class Binance:
    TRADING_FEE: float = 0.001  # 0.1% on every trade

    def __init__(self):
        self.base: str = "https://api.binance.com"
        self.trading_fee = Binance.TRADING_FEE
        self.endpoints: Dict[str, str] = {
            "klines": "/api/v3/klines",
            "price": "/api/v3/ticker/price"
        }

    def get_candlestick_data(self, symbol: str, interval: str = "1h", end_time: int = None,
                             limit: int = 1000) -> Union[DataFrame, int]:
        """
        Accesses candlestick data for a given symbol.

        Returns either a
            - DataFrame containing the candlestick data
            - Error code -1 in case of a failure
        """
        logger.info("Accessing candlestick data...")

        # Check whether we need to get more candlesticks than we can access with one API call (1000)
        if limit > 1000:
            return self.__get_coherent_candlestick_data(symbol, interval, limit, end_time)

        # Create url
        params: str = "?symbol=" + symbol + "&interval=" + interval + "&limit=" + str(limit)
        if end_time:
            params = params + "&endTime=" + str(int(end_time))
        url: str = self.base + self.endpoints["klines"] + params

        # Get data
        response: Response = requests.get(url)
        data: list = self.decode_http_response(response, url)
        if data == -1:
            return -1

        # Put data into a data frame and drop unnecessary columns, then rename them
        # [
        #   [
        #     1499040000000,      // Open time
        #     "0.01634790",       // Open
        #     "0.80000000",       // High
        #     "0.01575800",       // Low
        #     "0.01577100",       // Close
        #     "148976.11427815",  // Volume
        #     1499644799999,      // Close time
        #     "2434.19055334",    // Quote asset volume
        #     308,                // Number of trades
        #     "1756.87402397",    // Taker buy base asset volume
        #     "28.46694368",      // Taker buy quote asset volume
        #     "17928899.62484339" // Ignore.
        #   ]
        # ]

        df: DataFrame = DataFrame(data)
        df = df.drop(range(6, 12), axis=1)
        col_names: List[str] = ["time", "open", "high", "low", "close", "volume"]
        df.columns = col_names

        # Transform values from strings to floats
        for col in col_names:
            df[col] = df[col].astype(float)
        # Convert timestamps to datetime format and add them to the data frame
        df["date"] = pd.to_datetime(df["time"] / 1000, infer_datetime_format=True)

        return df

    def __get_coherent_candlestick_data(self, symbol: str, interval: str, limit: int = 1000, end_time: int = None
                                        ) -> DataFrame:
        """
        This function extends the "get_candlestick_data" function and it's purpose is for the accessing of long term
        market data. Binance only allows to get 1000 candles to be sent for one call. So if we want to collect market
        data over a long time span, we will have to make several calls for market data with each going backwards in time
        from the beginning of the previous market data. Then, all market data information will be merged into one long
        data frame.
        """
        logger.debug("Collecting longtime historical candlestick data...")

        repeat_rounds: int = 0
        if limit > 1000:
            repeat_rounds = int(limit / 1000)  # One round per 1000 candles
        initial_limit: int = limit % 1000
        if initial_limit == 0:
            initial_limit = 1000

        # First, we will get the last initial candles. E.g. if the limit is 5120 candles that we want to access, we will
        # start to get the market data for the 120 candles first in order to have clean values in steps of thousands
        # (like 5000). Then we can get the rest of the limit with the repeat rounds value accessing 1000 candles per
        # repeat round. The data will start at the end time going backwards (or starting in the present data if no end
        # time is specified
        df: DataFrame = self.get_candlestick_data(symbol, interval, end_time=end_time, limit=initial_limit)
        while repeat_rounds > 0:
            # Then, for every other 1000 candles, we get them, but starting at the beginning of the previously received
            # candles
            tmp_df: DataFrame = self.get_candlestick_data(symbol, interval, limit=1000, end_time=df["time"][0])
            df = tmp_df.append(df, ignore_index=True)
            repeat_rounds = repeat_rounds - 1
        return df

    def get_current_price(self, symbol: str = None) -> Union[int, List[Dict[str, str]], float]:
        """
        Returns the current price (float) for the given symbol.

        If no symbol is passed it will return the prices for all symbols within a list of dicts where each dict
        contains the symbol and its current price.

        Returns with error code -1 in case of failure.
        """
        logger.info(f"Accessing current price for symbol '{symbol}'")

        # Create URL
        url: str = self.base + self.endpoints["price"]
        if symbol:
            url = self.base + "?symbol=" + symbol

        # Get data
        response: Response = requests.get(url)
        data: Union[dict, list] = self.decode_http_response(response, url)
        if data == -1:
            return -1

        if type(data) == list:
            # Data contains list of dicts that contains prices for all symbols
            return data
        elif type(data) == dict:
            return float(data.get("price"))

    def decode_http_response(self, response: Response, url: str) -> Union[dict, list, int]:
        """
        Decodes the response text of a HTTP request.

        The return type is defined by the kind of JSON text that will be decoded:
        { "name":"John", "age":30, "car":null } -> dict
        [ "Ford", "BMW", "Fiat" ] -> list

        In case of exception returns with error code -1.
        """

        # Check the HTTP response and handle a possible BinanceAPIException
        try:
            self.__check_http_response(response)
        except BinanceAPIException as e:
            logger.error(f"BinanceAPIException occurred while trying to access {url}")
            logger.error(e.message)

        # Decode
        try:
            data: Union[Dict[str, str], List[Dict[str, str]]] = json.loads(response.text)
            return data
        except JSONDecodeError as e:
            logger.error(f"Could not decode content of GET response from {url}")
            logger.error(e.msg)
            return -1  # return with error code, because we cannot continue without data

    @staticmethod
    def __check_http_response(response: Response) -> None:
        """Checks status code of the HTTP response and raises a BinanceAPIException in case of error code."""
        if response.status_code >= 400:  # Status code signalizes error
            raise BinanceAPIException(response)
        elif response.status_code >= 500:  # Status code warns, failure is on site of Binance. Request might succeeded
            logger.warning("Internal Binance Error: Execution status unknown")
