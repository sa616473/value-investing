import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf

def get_balancesheet(ticker):
    stock_obj = yf.Ticker(ticker)
    return stock_obj.balancesheet

def income_statement(ticker):
    stock_obj = yf.Ticker(ticker)
    return stock_obj.financials

def get_info(ticker):
    df = {}
    ticker_info = yf.Ticker(ticker).info
    df['regularMarketPrice'] = ticker_info['regularMarketPrice']
    df['trailingEps'] = ticker_info['trailingEps']
    df['trailingAnnualDividendRate'] = ticker_info['trailingAnnualDividendRate']
    df['enterpriseValue'] = ticker_info['enterpriseValue']
    return df

def magic_formula(tickers):
    df = {}
    for ticker in tickers:
        print(ticker)
        balance_sheet = get_balancesheet(ticker).transpose()

        curr_assets = balance_sheet['Total Current Assets'].iloc[0]
        curr_liab = balance_sheet['Total Current Liabilities'].iloc[0]
        tang_assets = balance_sheet['Net Tangible Assets'].iloc[0]
        working_cap = curr_assets - curr_liab

        income_sheet = income_statement(ticker).transpose()

        EBIT = income_sheet['Ebit'].iloc[0]

        stats = get_info(ticker)
        ROIC = EBIT / (working_cap + tang_assets)
        EY_perc = (stats['trailingEps'] / stats['regularMarketPrice']) * 100
        EY = EBIT / stats['enterpriseValue']
        DivdendRate = stats['trailingAnnualDividendRate']
        df[ticker] = [EY_perc, EY, ROIC, DivdendRate, EBIT]
    
    df = pd.DataFrame(df).transpose()
    df.columns = ["EarningsYield%", "EarningsYield", "ReturnOnInvestedCapital", 'trailingAnnualDividendRate', "EBIT"]
    df["CombineRanking"] = df["EarningsYield"].rank(ascending=False,na_option='bottom') + df["ReturnOnInvestedCapital"].rank(ascending=False,na_option='bottom')
    df["Magic"] = df["CombineRanking"].rank(method='first')
    return df.sort_values("Magic")