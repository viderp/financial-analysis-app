# !pip install streamlit
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf # https://pypi.org/project/yfinance/
import string
from ta.volatility import BollingerBands
from ta.trend import MACD
from ta.momentum import RSIIndicator
from pandas import DataFrame


##################
# Set up sidebar #
##################

# Add in location to select image.

st.title('Company overview')

option = st.sidebar.text_input('Please enter your company ticker:','AAPL')
company = yf.Ticker(option)
descreption = company.info["longBusinessSummary"]
st.write(descreption)

import datetime

today = datetime.date.today()
before = today - datetime.timedelta(days=700)
start_date = st.sidebar.date_input('Start date', before)
end_date = st.sidebar.date_input('End date', today)
if start_date < end_date:
    st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.sidebar.error('Error: End date must fall after start date.')


##############
# Stock data #
##############

# https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#momentum-indicators

df = yf.download(option,start= start_date,end= end_date, progress=False)

indicator_bb = BollingerBands(df['Close'])

bb = df
bb['bb_h'] = indicator_bb.bollinger_hband()
bb['bb_l'] = indicator_bb.bollinger_lband()
bb = bb[['Close','bb_h','bb_l']]

macd = MACD(df['Close']).macd()

rsi = RSIIndicator(df['Close']).rsi()


###################
# Set up main app #
###################

st.subheader('Stock Bollinger Bands')

st.line_chart(bb)

progress_bar = st.progress(0)

# https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py

st.subheader('Stock Moving Average Convergence Divergence (MACD)')
st.area_chart(macd)

st.subheader('Stock RSI ')
st.line_chart(rsi)


st.subheader('Recent data ')
st.dataframe(df.tail(10))


################
# Download csv #
################

import base64
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="download.xlsx">Download excel file</a>' # decode b'abc' => abc

st.markdown(get_table_download_link(df), unsafe_allow_html=True)


### financial data
st.subheader("Balance Sheet")
st.write(company.balance_sheet)
get_table_download_link(company.balance_sheet)
st.markdown(get_table_download_link(company.balance_sheet), unsafe_allow_html=True)

st.subheader("Cashflow Statement")
st.write(company.cashflow)
get_table_download_link(company.cashflow)
st.markdown(get_table_download_link(company.cashflow), unsafe_allow_html=True)

st.subheader("Other financial data")
st.write(company.financials)
get_table_download_link(company.financials)
st.markdown(get_table_download_link(company.financials), unsafe_allow_html=True)


##DCF
st.header("Discounted Cash Flow (DCF)")
st.write("Discounted cash flow (DCF) is a valuation method used to estimate the value of an "
         "investment based on its expected future cash flows. DCF analysis attempts to figure out the value of an "
         "investment today, based on projections of how much money it will generate in the future. This applies to "
         "the decisions of investors in companies or securities, such as acquiring a company or buying a stock, "
         "and for business owners and managers looking to make capital budgeting or operating expenditures decisions.")

st.subheader("KEY TAKEAWAYS")
st.write( "1. Discounted cash flow (DCF) helps determine the value of an investment based on its future cash flows.")
st.write("2. The present value of expected future cash flows is arrived at by using a discount rate to calculate "
         "the DCF. ")
st.write("3. If the DCF is above the current cost of the investment, the opp ortunity could result in positive "
         "returns. ")
st.write("4. Companies typically use the weighted average cost of capital (WACC) for the discount rate, because "
         "it takes into consideration the rate of return expected by shareholders.")
st.write("5. The DCF has limitations, primarily in that it relies on estimations of future cash flows, which "
                  "could prove inaccurate.")

##formula

st.subheader("Discounted Cash Flow Formula")
st.write("The formula for DCF is")
st.write("DCF = CF1/(1+r) + CF2/(1+r) + CFn/(1+r)")
st.write("Where")
st.write("CF = The cash flow for the given year")
st.write("r = The discount rate")


r_interest = st.number_input('Please enter risk free interest rate:',0.04)
r_growth = st.number_input('Please enter growth rate of net cash flow:',0.01)

# net cash flow calculation
cash_flow = DataFrame(company.cashflow)
op_cf = cash_flow.loc["Total Cash From Operating Activities"]
capex = cash_flow.loc["Capital Expenditures"]
net_cf = op_cf + capex
flow_table = DataFrame(net_cf)
flow_table.columns = ["The net cashflow of the company recently years"]
st.write(flow_table)

## net present value (NPV)

cf_av = (net_cf[0] + net_cf[1] + net_cf[2])/3

npv = cf_av/(r_interest - r_growth)

st.subheader("The Net Present Value of the company")
st.write(npv)

## The price prediction
st.subheader("The fair value to buy")
shares = company.info["sharesOutstanding"]
st.write(npv / shares)

st.subheader("The current stock price")
st.write(company.info["currentPrice"])

