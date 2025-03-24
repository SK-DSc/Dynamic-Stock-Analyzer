import streamlit as st
import pandas as pd
from utils import fetch_stock_data, fetch_financial_metrics

def main():
    st.title("Dynamic Stock Analysis using LLM")
    
    stock1 = st.text_input("Enter First Stock Symbol (e.g., AAPL)")
    stock2 = st.text_input("Enter Second Stock Symbol (e.g., MSFT)")
    timeframe = st.selectbox("Select Timeframe", ["3 months", "6 months", "1 year", "5 years", "10 years"])
    
    if st.button("Analyze"):
        if stock1 and stock2:
            data1 = fetch_stock_data(stock1, period='1y')
            data2 = fetch_stock_data(stock2, period='1y')
            
            st.subheader(f"Stock Performance of {stock1} and {stock2}")
            st.line_chart(pd.DataFrame({stock1: data1['Close'], stock2: data2['Close']}))
            
            st.subheader("Financial Metrics Comparison")
            metrics1 = fetch_financial_metrics(stock1)
            metrics2 = fetch_financial_metrics(stock2)
            st.write(pd.DataFrame({stock1: metrics1, stock2: metrics2}))
        else:
            st.warning("Please enter both stock symbols.")

if __name__ == "__main__":
    main()
