import requests
import logging
import pandas as pd

from datetime import datetime
from typing import List, Dict, Union
from pandas import DataFrame
from logging import Logger
from requests.models import Response
from json.decoder import JSONDecodeError

logger: Logger = logging.getLogger("__main__")


class Binance:
    TRADING_FEE: float = 0.001  # 0.1% on every trade

    # Symbols
    SYMBOL_BITCOIN_EURO: str = "BTCEUR"
    SYMBOL_ETHEREUM_EURO: str = "ETHEUR"
    SYMBOL_LITECOIN_EURO: str = "LTCEUR"

    # Order sides
    SIDE_BUY: str = "BUY"
    SIDE_SELL: str = "SELL"

    # Order types
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_STOP_LOSS = "STOP_LOSS"
    ORDER_TYPE_STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    ORDER_TYPE_TAKE_PROFIT = "TAKE_PROFIT"
    ORDER_TYPE_TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"
    ORDER_TYPE_LIMIT_MAKER = "LIMIT_MAKER"

    # Endpoints
    ENDPOINT_KLINES = "/api/v3/klines"
    ENDPOINT_PRICE = "/api/v3/ticker/price"
    ENDPOINT_TIME = "/api/v3/time"
    ENDPOINT_TEST_ORDER = "/api/v3/order/test"
    ENDPOINT_EXCHANGE_INFO = "/api/v3/exchangeInfo"

    # Filter types
    FILTER_TYPE_PRICE_FILTER = "PRICE_FILTER"
    FILTER_TYPE_LOT_SIZE = "LOT_SIZE"

    def __init__(self):
        self.base: str = "https://api.binance.com"
        self.trading_fee = Binance.TRADING_FEE

    def get_candlestick_data(self, symbol: str, interval: str = "1h", end_time: int = None,
                             limit: int = 1000) -> Union[DataFrame, bool]:
        """
        Accesses candlestick data for a given symbol.

        Returns:
            - DataFrame containing the candlestick data
            - False in case of a failure
        """
        logger.info("Accessing candlestick data...")

        # Check whether we need to get more candlesticks than we can access with one API call (1000)
        if limit > 1000:
            return self.__get_coherent_candlestick_data(symbol, interval, limit, end_time)

        # Get data
        params: List[str] = [
            "symbol=" + symbol,
            "interval=" + interval,
            "limit=" + str(limit)
        ]
        if end_time:
            params.append("endTime=" + str(end_time))
        data: Union[dict, list, bool] = self.http_request(endpoint=self.ENDPOINT_KLINES, params=params)
        if not data:
            logger.error("Missing candlestick data")
            return False

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
        Accesses long term historical candlestick market data.

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
        # start to get the market data for the 120 candles first, in order to have clean values in steps of thousands
        # (like 5000). Then we can get the rest of the limit with the repeat rounds value accessing 1000 candles per
        # repeat round. The data will start at the end time going backwards (or starting in the present data if no end
        # time is specified
        df: DataFrame = self.get_candlestick_data(symbol, interval, end_time=end_time, limit=initial_limit)
        while repeat_rounds > 0:
            # Then, for every other 1000 candles, we get them, but starting at the beginning of the previously received
            # candles
            tmp_df: DataFrame = self.get_candlestick_data(symbol, interval, limit=1000, end_time=int(df["time"][0]))
            tmp_df.drop(tmp_df.tail(1).index, inplace=True)
            df = tmp_df.append(df, ignore_index=True)
            repeat_rounds = repeat_rounds - 1
        return df

    def get_current_price(self, symbol: str = None) -> Union[List[Dict[str, str]], float, bool]:
        """
        Returns the current price (float) for the given symbol.

        If no symbol is passed it will return the prices for all symbols within a list of dicts where each dict
        contains the symbol and its current price.

        Returns false in case of failure.
        """
        logger.info(f"Accessing current price for symbol '{symbol}'")

        # Get data
        params: List[str] = ["symbol=" + symbol]
        data: Union[dict, list, bool] = self.http_request(endpoint=self.ENDPOINT_PRICE, params=params)
        if not data:
            logger.error("Missing price data")
            return False

        if type(data) == list:
            # Data contains list of dicts that contains prices for all symbols
            return data
        elif type(data) == dict:
            return float(data.get("price"))

    def get_server_time(self) -> Union[datetime, bool]:
        """
        Get current Binance server time.

        Returns:
            - Server time in datetime format
            - False in case of error
        """

        # Get data
        data: Union[dict, list, bool] = self.http_request(endpoint=self.ENDPOINT_TIME)
        if not data:
            logger.error("Missing server time data")
            return False

        time: datetime = datetime.fromtimestamp(data.get("serverTime") / 1000)
        return time

    def __get_exchange_info(self) -> Union[Dict, bool]:
        """
        Get exchange trading rules and symbol information on all currently tradable symbols.

        Returns:
            - Exchange information as dict
            - False in case of error
        """
        # Get data
        data: Union[dict, list, bool] = self.http_request(endpoint=self.ENDPOINT_EXCHANGE_INFO)
        if not data:
            logger.error("Missing exchange info data")
            return False
        else:
            return data

    def __get_symbol_data(self, symbol: str) -> Dict[str, Union[str, list]]:
        """
        Returns all symbol data for a given symbol.

        {
          "symbol": "ETHBTC",
          "status": "TRADING",
          "baseAsset": "ETH",
          "baseAssetPrecision": 8,
          "quoteAsset": "BTC",
          "filters": [
            ...
          ],
          ...
        }
        """
        exchange_info: Dict = self.__get_exchange_info()
        # Get list of dicts where each dict contains data for one symbol
        symbols: List[Dict[str, str]] = exchange_info.get("symbols")
        for symbol_data in symbols:
            # Loop through all symbol data until we have found the data for the symbol we search for
            if symbol_data.get("symbol") == symbol:
                return symbol_data

    def get_symbol_filters(self, symbol: str) -> List[Dict[str, str]]:
        """
        Returns all filters (trading rules) for a given symbol.

        "filters": [
            {
              "filterType": "MARKET_LOT_SIZE",
              "minQty": "0.00100000",
              "maxQty": "100000.00000000",
              "stepSize": "0.00100000"
            },
            ...
        ],
        """
        symbol_data: Dict[str, Union[str, list]] = self.__get_symbol_data(symbol)
        filters: List[Dict[str, str]] = symbol_data.get("filters")
        return filters

    def http_request(self, endpoint: str, params: List[str] = None) -> Union[dict, list, bool]:
        """
        Creates and executes a HTTP request with the given url and parameters.

        The return type is defined by the kind of JSON text that will be decoded:
        { "name":"John", "age":30, "car":null } -> dict
        [ "Ford", "BMW", "Fiat" ] -> list

        Returns false in case of exception.
        """
        # Create URL
        url: str = self.base + endpoint
        for i in range(len(params)):
            if i == 0:
                # First param has to connect with a question mark to the url
                url = url + "?" + params[i]
            else:
                # Other params connect with a ampersand
                url = url + "&" + params[i]
        logger.debug(f"Calling {url}...")

        # Call url to get excepted response
        try:
            response: Response = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"ConnectionError: {e}")
            return False

        # Check response
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return False

        # Decode data
        try:
            data: Union[Dict[str, str], List[Dict[str, str]]] = response.json()
        except JSONDecodeError as e:
            logger.error(f"Could not decode data from {url}: {e}")
            return False
        else:
            return data
