import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

class OrderBlocksIndicator:
    def __init__(self, ticker, candle_range=15, show_pd=False, show_bearish_bos=False, show_bullish_bos=False):
        self.ticker = ticker
        self.candle_range = candle_range
        self.show_pd = show_pd
        self.show_bearish_bos = show_bearish_bos
        self.show_bullish_bos = show_bullish_bos
        self.df = self.fetch_data()
        self.fig = go.Figure()

    def fetch_data(self):
        data = yf.download(self.ticker, start="2023-01-16", end="2024-01-16")
        return data

    def structure_low_index_pointer(self, length):
        min_value = self.df['High'].rolling(window=length).max().shift(1)
        min_index = min_value.idxmin()
        return min_index

    def plot_order_blocks(self):
        long_boxes = []
        short_boxes = []
        bos_lines = []

        last_down_index = 0
        last_down = 0
        last_low = 0

        last_up_index = 0
        last_up = 0
        last_up_low = 0
        last_up_open = 0
        last_high = 0
        last_bull_break_low = 0

        structure_low_index = 0
        structure_low = 1000000

        for i in range(len(self.df)):
            if self.df['Low'][i] < structure_low:
                structure_low = self.df['Low'][i]
                structure_low_index = self.structure_low_index_pointer(self.candle_range)

            if self.df['Low'][i] < structure_low:
                if (i - last_up_index) < 1000:
                    short_boxes.append(dict(x0=last_up_index, x1=last_up_index, y0=last_high, y1=last_up_low,
                                            fillcolor='rgba(255,0,0, 0.9)', line=dict(color='rgba(255,0,0, 0.9)'),
                                            xref='x', yref='y'))

                    if self.show_bearish_bos:
                        bos_lines.append(
                            dict(x=[structure_low_index, i], y=[structure_low, structure_low], mode='lines',
                                 line=dict(color='red', width=2)))

                    self.plot_candle(i, CandleColourMode=0, show_bos_candle=True, CandleColour='rgba(255,0,0, 0.9)')
                    last_short_index = last_up_index

            if len(short_boxes) > 0:
                for j in range(len(short_boxes) - 1, -1, -1):
                    box = short_boxes[j]
                    top = box['y1']
                    left = box['x0']
                    if self.df['Close'][i] > top:
                        short_boxes.pop(j)
                        if (i - last_down_index) < 1000 and i > last_long_index:
                            long_boxes.append(dict(x0=last_down_index, x1=last_down_index, y0=last_down, y1=last_low,
                                                   fillcolor='rgba(0,255,0, 0.9)', line=dict(color='rgba(0,255,0, 0.9)'),
                                                   xref='x', yref='y'))

                            if self.show_bullish_bos:
                                bos_lines.append(
                                    dict(x=[left, i], y=[top, top], mode='lines', line=dict(color='green', width=1)))

                            self.plot_candle(i, CandleColourMode=1, show_bos_candle=True, CandleColour='rgba(0,255,0, 0.9)')
                            last_long_index = i
                            last_bull_break_low = self.df['Low'][i]

            if len(long_boxes) > 0:
                for j in range(len(long_boxes) - 1, -1, -1):
                    lbox = long_boxes[j]
                    bottom = lbox['y1']
                    top = lbox['y0']
                    if self.df['Close'][i] < bottom:
                        long_boxes.pop(j)

            self.plot_candle(i, CandleColourMode=1 if self.df['Close'][i] > self.df['Open'][i] else 0,
                             show_bos_candle=False)

            if self.df['Close'][i] < self.df['Open'][i]:
                last_down = self.df['High'][i]
                last_down_index = i
                last_low = self.df['Low'][i]

            if self.df['Close'][i] > self.df['Open'][i]:
                last_up = self.df['Close'][i]
                last_up_index = i
                last_up_open = self.df['Open'][i]
                last_up_low = self.df['Low'][i]
                last_high = self.df['High'][i]

            last_high = max(self.df['High'][i], last_high)
            last_low = min(self.df['Low'][i], last_low)

        self.fig.show()

    def plot_candle(self, i, CandleColourMode, show_bos_candle=False):
        candle = go.Candlestick(
            x=[i],
            open=[self.df['Open'][i]],
            high=[self.df['High'][i]],
            low=[self.df['Low'][i]],
            close=[self.df['Close'][i]],
            hoverinfo='x+y+z',
            increasing_line_color='green',
            decreasing_line_color='red',
            increasing_fillcolor='rgba(0,255,0, 0.9)',  # Змінено fillcolor на increasing_fillcolor
            decreasing_fillcolor='rgba(255,0,0, 0.9)'  # Змінено fillcolor на decreasing_fillcolor
        )

        self.fig.add_trace(candle)

        if show_bos_candle:
            self.fig.add_trace(
                go.Candlestick(
                    x=[i],
                    open=[self.df['Open'][i]],
                    high=[self.df['High'][i]],
                    low=[self.df['Low'][i]],
                    close=[self.df['Close'][i]],
                    hoverinfo='x+y+z',
                    increasing_line_color='green',
                    decreasing_line_color='red',
                    increasing_fillcolor='rgba(0,255,0, 0.9)',
                    decreasing_fillcolor='rgba(255,0,0, 0.9)'
                )
            )




if __name__ == "__main__":
    indicator = OrderBlocksIndicator(ticker="AAPL", candle_range=15, show_pd=False, show_bearish_bos=False,
                                     show_bullish_bos=False)
    indicator.plot_order_blocks()
