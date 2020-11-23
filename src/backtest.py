import logging
import plotly.graph_objs as go

from datetime import datetime
from logging import Logger
from plotly.graph_objs import Candlestick, Layout, Figure, Scatter
from plotly.offline import plot
from typing import List
from market_data import MarketData
from indicators import SmoothedMovingAverage
from transaction import Transaction

logger: Logger = logging.getLogger(__name__)


class Backtest:

    @staticmethod
    def plot_candlestick_chart(market_data: MarketData, plot_title: str, buy_transactions: List[Transaction] = None,
                               sell_transactions: List[Transaction] = None) -> None:
        """Plots a candlestick chart"""
        logger.info("Plotting candlestick chart...")

        # Access candlestick data frame which gets hold by the market data object
        df = market_data.candlestick_data

        # Plot candlestick chart
        candle: Candlestick = Candlestick(
            x=df["time"],
            open=df["open"],
            close=df["close"],
            high=df["high"],
            low=df["low"],
            name="Candlesticks"
        )
        data: List[object] = [candle]

        # Loop through all indicators of the market data and plot them
        for indicator in market_data.indicators:
            # Smoothed moving average
            if type(indicator) == SmoothedMovingAverage:
                sma: Scatter = go.Scatter(
                    x=df["time"],
                    y=df[indicator.get_name()],
                    name=indicator.get_name(),
                    line=dict(color="rgba(255, 207, 102, 1)")
                )
                data.append(sma)
            # Continue with other indicator types for plotting:
            # if type(indicator) == Indicator...

        # Plot buy transactions if we pass them
        if buy_transactions:
            times: List[datetime] = list()
            prices: List[float] = list()

            for transaction in buy_transactions:
                times.append(transaction.time)
                prices.append(transaction.price)

            buys: Scatter = Scatter(
                x=times,
                y=prices,
                name="Buy Transactions",
                mode="markers",
                line=dict(color="rgba(138, 43, 226, 1)")
            )
            data.append(buys)

        # Plot sell transactions if we pass them
        if sell_transactions:
            times: List[datetime] = list()
            prices: List[float] = list()

            for transaction in sell_transactions:
                times.append(transaction.time)
                prices.append(transaction.price)

            sells: Scatter = Scatter(
                x=times,
                y=prices,
                name="Sell Transactions",
                mode="markers",
                line=dict(color="rgba(139, 69, 19, 1)")
            )
            data.append(sells)

        # Customize style and display
        layout: Layout = Layout(
            xaxis={
                "title": "Time(UTC): European Wintertime(UTC+1); European Summertime(UTC+2)",
                "rangeslider": {"visible": True},
                "type": "date"
            },
            yaxis={
                "fixedrange": False,
                "title": "Price"
            }
        )

        # Create figure and plot it
        figure: Figure = Figure(data=data, layout=layout)
        plot(figure, filename=plot_title + ".html")
