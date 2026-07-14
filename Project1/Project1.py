# Python - start 7/12 - end 
#  Beginning project with yfinance and others to learn and possibly  QuantLib and pyql


import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="AAPL Market Dashboard",
    page_icon="🍎 🍏 🧺",
    layout="wide",
)

st.title("Apple Market Dashboard")
st.caption("Interactive AAPL market data dashboard powered by yfinance (yippee)")

st.sidebar.header("Dashboard Controls 🍎")
period = st.sidebar.selectbox(
    "Time Period",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    index=3,
)

interval = st.sidebar.selectbox(
    "Data Interval",
    options=["1d", "1wk", "1mo"],
    index=0
)
show_sma_20 = st.sidebar.checkbox("Show 20-Period SMA", value=True)
show_sma_50 = st.sidebar.checkbox("Show 50-Period SMA", value=True)
show_volume = st.sidebar.checkbox("Show Volume", value=True)

@st.cache_data(ttl=300)
def load_stock_data(
    ticker_symbol: str,
    selected_period: str,
    selected_interval: str,
) -> pd.DataFrame:
    """
    Download historical market data.
    The cache expires after 300 seconds so the application does not repeatedly contact Yahoo Finance during every Streamlit rerun."""""
    
    data = yf.download(
        ticker_symbol,
        period=selected_period,
        interval=selected_interval,
        auto_adjust=False,
        progress=False        
    )
    if data.empty:
        return data
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    data = data.reset_index()
    
    data["SMA 20"] = data["Close"].rolling(window=20).mean()
    data["SMA 50"]= data["Close"].rolling(window=50).mean()
    data["Daily Return"]=data["Close"].pct_change()
    
    return data

try:
    stock_data = load_stock_data("AAPL", period, interval)
except Exception as error:
    st.error(f"Unable to retrieve AAPL data: {error}")
    st.stop
    
#metrics yippee

latest_close = float(stock_data["Close"].iloc[-1])

if len(stock_data) > 1:
    previous_close = float(stock_data["Close"].iloc[-2])
    price_change = latest_close - previous_close
    percent_change = ( price_change / previous_close) * 100
else:
    price_change = 0.0
    percent_change = 0.0
    
period_high = float(stock_data["High"].max())
period_low = float(stock_data["Low"].min())
average_volume = float(stock_data["Volume"].mean())

metric_1, metric_2, metric_3, metric_4 = st.columns(4)

metric_1.metric(
    label="Latest close",
    value=f"${latest_close:,.2f}",
    delta=f"{price_change:+.2f} ({percent_change:.2f}%)"
)

metric_2.metric(
    label="Period High",
    value=f"${period_high:,.2f}"   
)

metric_3.metric(
    label="Period Low",
    value=f"${period_low:,.2f}"
)

metric_4.metric(
    label="Average volume",
    value=f"{average_volume:,.0f}"
)

price_figure = go.Figure()
# HAHA go figure

price_figure.add_trace(
    go.Candlestick(
        x = stock_data["Date"],
        open = stock_data["Open"],
        high=stock_data["High"],
        low=stock_data["Low"],
        close=stock_data["Close"],
        name="AAPL"
    )
)

if show_sma_20:
    price_figure.add_trace(
        go.Scatter(
            x=stock_data["Date"],
            y=["SMA 20"],
            mode = "lines",
            name = "SMA 20"
        )
    )

if show_sma_50:
    price_figure.add_trace(
        go.Scatter(
            x=stock_data["Date"],
            y=["SMA 50"],
            mode = "lines",
            name = "SMA 50"
        )
    )
    
price_figure.update_layout(
    title=f"AAPL Price: {period}",
    xaxis_title = "Date",
    yaxis_title = "Price (USD)",
    height = 600,
    xaxis_rangeslider_visible=False,
    hovermode="x unified"
)

st.plotly_chart(
    price_figure,
    use_container_width=True
)

overview_tab, returns_tab, data_tab = st.tabs(
    ["Volume", "Returns", "Raw Data"]
)

with overview_tab:
    if show_volume:
        volume_figure = go.Figure()
        
        volume_figure.add_trace(
            go.Bar(
                x = stock_data["Date"],
                y = stock_data["Volume"],
                name = "Volume"
            )
        )
        volume_figure.update_layout(
            title="AAPL Trading Volume",
            xaxis_title="Date",
            yaxis_title="Shares",
            height=400
        )
        st.plotly_chart(
            volume_figure,
            use_container_width=True
        )
    else:
        st.info("Enable the volume in the sidebar to display this chart. 🍎")
        

with returns_tab:
    returns_figure = go.Figure()
    # its still silly
    returns_figure.add_trace(
        go.Scatter(
            x=stock_data["Date"],
            y=stock_data["Daily Return"] * 100,
            mode="lines",
            name="Return"
        )
        
    )
    returns_figure.update_layout(
        title="AAPL Period-to-Period Returns🍎",
        xaxis_title="Date",
        yaxis_title="Return (%)",
        height = 400,
        hovermode="x unified",
    )
    st.plotly_chart(
        returns_figure,
        use_container_width=True
    )
    volatility = stock_data["Daily Return"].std()* np.sqrt(252) * 100
    
    st.metric(
        label="Annualized historical volatility",
        value=f"{volatility:.2f}%"
    )
    
with data_tab:
    st.dataframe(
        stock_data.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )
    csv_data = stock_data.to_csv(index=False).encode("utf-8")
    
    st.download_button(
        label="Download AAPL data as CSV 🍎",
        data=csv_data,
        file_name="AAPL_Market_Data.csv",
        mime="text/csv"
    )
    
st.caption(
    f"Last dashboard refresh: {datetime.now():%Y-%m-%d %H:%M:%S}"
)