import streamlit as st
import traceback
import yfinance as yf
import pandas as pd
from yahooquery import Screener
from openai import OpenAI
client = OpenAI(api_key=st.secrets["llm_api_key"], base_url="https://api.deepseek.com")

# Mapping countries to Yahoo Finance screener codes
COUNTRY_MAPPING = {
    "United States": "most_actives",  # No specific US tag available
    "Canada": "most_actives_ca",
    "United Kingdom": "most_actives_gb",
    "Australia": "most_actives_au",
    "Germany": "most_actives_de",
    "France": "most_actives_fr",
    "India": "most_actives_in",
    "Brazil": "most_actives_br",
    "Hong Kong": "most_actives_hk",
    "Singapore": "most_actives_sg",
    "Spain": "most_actives_es",
    "Italy": "most_actives_it"
}


# Fallback Indexes (Major Market Indices)
FALLBACK_INDEXES = {
    "United States": "^GSPC",  # S&P 500
    "Canada": "^GSPTSE",  # S&P/TSX Composite Index
    "United Kingdom": "^FTSE",  # FTSE 100
    "Australia": "^AXJO",  # ASX 200
    "Germany": "^GDAXI",  # DAX 40
    "France": "^FCHI",  # CAC 40
    "Japan": "^N225",  # Nikkei 225
    "India": "^BSESN",  # BSE Sensex
    "China": "000001.SS",  # SSE Composite Index
    "Brazil": "^BVSP",  # Bovespa Index
    "South Korea": "^KS11",  # KOSPI Index
    "Hong Kong": "^HSI",  # Hang Seng Index
    "Singapore": "^STI",  # Straits Times Index
    "Mexico": "^MXX",  # IPC (Mexican Stock Exchange)
    "Italy": "^FTMIB",  # FTSE MIB Index
    "Spain": "^IBEX",  # IBEX 35
    "Netherlands": "^AEX",  # AEX Index
    "Sweden": "^OMXS30",  # OMX Stockholm 30
    "Switzerland": "^SSMI",  # Swiss Market Index
    "Russia": "IMOEX.ME",  # MOEX Russia Index
    "South Africa": "J203.JO",  # FTSE/JSE Top 40
}


def get_top_stocks(country):
    '''Fetch top 10 most active stocks or fallback to major index constituents.'''
    screener_key = COUNTRY_MAPPING.get(country)

    try:
        # 🔹 Attempt 1: YahooQuery Screener
        s = Screener()
        screeners = s.get_screeners(screener_key, count=200)
        quotes = screeners.get(screener_key, {}).get("quotes", [])

        if quotes:
            return {quote.get("shortName", "Unknown"): quote.get("symbol", "N/A") for quote in quotes}

        # 🔹 Attempt 2: Fallback Index
        index_symbol = FALLBACK_INDEXES.get(country)
        if index_symbol:
            index_data = yf.Ticker(index_symbol).constituents
            if index_data:
                return {yf.Ticker(stock).info.get("shortName", stock): stock for stock in list(index_data.keys())}

    except Exception as e:
        print(f"Error fetching stocks for {country}: {e}")

    return {"No Stocks Found": "N/A"}  # If all fails

def get_stock_data(stock_symbol, period):
    '''Fetch historical stock data using Yahoo Finance.'''
    try:
        stock = yf.Ticker(stock_symbol)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        print(f"Error fetching stock data for {stock_symbol}: {e}")
        return pd.DataFrame()

def calculate_investment_growth(stock_data):
    '''Calculate the value of 100 INR/USD invested at the selected timeframe.'''
    if stock_data.empty or "Close" not in stock_data:
        return None
    initial_price = stock_data["Close"].iloc[0]
    normalized_values = (stock_data["Close"] / initial_price) * 100
    return normalized_values

def classify_market_cap(market_cap):
    '''Classify market capitalization as Large Cap, Mid Cap, or Small Cap.'''
    if market_cap is None:
        return "N/A"
    elif market_cap > 10e9:
        return f"Large Cap ({market_cap/1e9:.2f}B)"
    elif market_cap > 2e9:
        return f"Mid Cap ({market_cap/1e9:.2f}B)"
    else:
        return f"Small Cap ({market_cap/1e9:.2f}B)"


def compare_stocks(stock1_name, stock1_info, stock2_name, stock2_info):
    '''Compare two stocks and display a structured table with an interpretation column and better stock marked'''

    # Define metric interpretations
    metric_interpretations = {
        "MARKET CAP": "Higher is better (indicates stocks risk factor)"
        "EPS": "Higher is better (indicates profitability)",
        "P/E Ratio": "Lower is better (cheaper valuation)",
        "ROE (%)": "Higher is better (profitability efficiency)",
        "ROA (%)": "Higher is better (asset efficiency)",
        "Net Profit Margin (%)": "Higher is better (profitability measure)",
    }

    # Extract relevant metrics, defaulting to 'N/A' if missing
    stock1_data = {
        "MARKET CAP": stock1_info.get("marketcap", "N/A"),
        "EPS": stock1_info.get("trailingEps", "N/A"),
        "P/E Ratio": stock1_info.get("trailingPE", "N/A"),
        "ROE (%)": stock1_info.get("returnOnEquity", "N/A"),
        "ROA (%)": stock1_info.get("returnOnAssets", "N/A"),
        "Net Profit Margin (%)": stock1_info.get("profitMargins", "N/A"),
    }

    stock2_data = {
        "MARKET CAP": stock2_info.get("marketcap", "N/A"),
        "EPS": stock2_info.get("trailingEps", "N/A"),
        "P/E Ratio": stock2_info.get("trailingPE", "N/A"),
        "ROE (%)": stock2_info.get("returnOnEquity", "N/A"),
        "ROA (%)": stock2_info.get("returnOnAssets", "N/A"),
        "Net Profit Margin (%)": stock2_info.get("profitMargins", "N/A"),
    }

    # Create comparison table
    comparison_data = []

    for metric in stock1_data.keys():
        value1 = stock1_data[metric]
        value2 = stock2_data[metric]
        interpretation = metric_interpretations.get(metric, "N/A")

        # Determine the better stock (higher is better, except for P/E Ratio)
        if value1 == "N/A" or value2 == "N/A":
            better_stock = "N/A"
        elif metric == "P/E Ratio":  # Lower is better for P/E Ratio
            better_stock = stock1_name if value1 < value2 else stock2_name
        else:  # Higher is better for other metrics
            better_stock = stock1_name if value1 > value2 else stock2_name

        # Append row data
        comparison_data.append([
            metric,
            interpretation,
            f"{value1} {'✅' if better_stock == stock1_name else ''}",
            f"{value2} {'✅' if better_stock == stock2_name else ''}"
        ])

    # Convert to DataFrame
    comparison_df = pd.DataFrame(comparison_data, columns=["Metric", "Interpretation", stock1_name, stock2_name])

    # Display the table in Streamlit
    st.write("### Stock Comparison Table")
    st.table(comparison_df)


    # Determine the overall better stock (based on majority of metrics)
    stock1_wins = sum(1 for row in comparison_data if "✅" in row[1])
    stock2_wins = sum(1 for row in comparison_data if "✅" in row[2])

    overall_best = stock1_name if stock1_wins > stock2_wins else stock2_name
    second_best = stock2_name if stock1_wins > stock2_wins else stock1_name
    st.write(f"### Conclusion: The  **{overall_best}** is having better financial metrics than **{second_best}**.")


import requests
def get_llm_analysis(stock1_name, stock1_info, stock2_name, stock2_info):
    '''Fetch LLM-based investment insights from Hugging Face API.'''
    try:
        prompt = f'''
        Analyze and compare {stock1_name} and {stock2_name} as investment opportunities. Output a comprehensive analysis based on financial metrics, market trends, and future growth prospects.
        The following informations are available:
        {stock1_name}: {stock1_info},
        {stock2_name}: {stock2_info}'''
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a prudent technical stock investor and advisor"},
                {"role": "user", "content": prompt},
            ],
            stream=False)
        # 🔍 Debugging: Print API Response
        #print("🔹 LLM API Raw Response:", response.choices[0].message.content)

        # Ensure the API response is valid JSON
        response_text=response.choices[0].message.content

        return response_text if response_text else "No AI insights available."

    except Exception as e:
        return f"AI analysis failed due to an error: {e}"


def generate_conclusion(stock1_name, stock1_info, stock2_name, stock2_info):
    '''Compare two stocks based on financial metrics and determine the better investment with Min-Max scaling.'''

    def min_max_scaling(value, min_val, max_val):
        '''Apply Min-Max scaling to normalize values between 0 and 1.'''
        if max_val - min_val == 0:
            return 0  # Avoid division by zero
        return (value - min_val) / (max_val - min_val)

    def calculate_score(stock_info, min_max_values):
        '''Calculate stock score based on Market Cap, P/E Ratio, EPS, and ROE using Min-Max scaling.'''
        try:
            market_cap = stock_info.get("marketCap", 0) / 1e9  # Convert to billions
            pe_ratio = stock_info.get("trailingPE", float("inf"))  # Avoid division by zero
            eps = stock_info.get("trailingEps", 0)
            roe = stock_info.get("returnOnEquity", 0)

            # Min-Max Scaling
            market_cap = min_max_scaling(market_cap, *min_max_values["marketCap"])
            pe_ratio = min_max_scaling(1 / pe_ratio if pe_ratio > 0 else 0, *min_max_values["peRatio"])
            eps = min_max_scaling(eps, *min_max_values["eps"])
            roe = min_max_scaling(roe, *min_max_values["roe"])

            # Apply the scoring formula
            score = market_cap + pe_ratio + eps + roe
            return score
        except Exception as e:
            print(f"Error in scoring: {e}")
            st.write(traceback.format_exc())
            return 0  # Return 0 if any calculation fails

    # Extract raw values for scaling
    stock_values = {
        "marketCap": [stock1_info.get("marketCap", 0) / 1e9, stock2_info.get("marketCap", 0) / 1e9],
        "peRatio": [1 / stock1_info.get("trailingPE", float("inf")) if stock1_info.get("trailingPE", float("inf")) > 0 else 0,
                    1 / stock2_info.get("trailingPE", float("inf")) if stock2_info.get("trailingPE", float("inf")) > 0 else 0],
        "eps": [stock1_info.get("trailingEps", 0), stock2_info.get("trailingEps", 0)],
        "roe": [stock1_info.get("returnOnEquity", 0), stock2_info.get("returnOnEquity", 0)]
    }

    # Compute min-max values for scaling
    min_max_values = {key: (min(values), max(values)) for key, values in stock_values.items()}

    # Calculate scores for both stocks using Min-Max scaled values
    try:
        score1 = calculate_score(stock1_info, min_max_values)
        score2 = calculate_score(stock2_info, min_max_values)
    except:
        st.write(traceback.format_exc())

    # Handle None values by setting defaults
    stock1_name = stock1_name or "N/A"
    stock2_name = stock2_name or "N/A"
    score1 = score1 if score1 is not None else 0
    score2 = score2 if score2 is not None else 0

    # Determine the better stock
    better_stock = stock1_name if score1 > score2 else stock2_name
    score_difference = abs(score1 - score2)

    # 🛠 Debugging: Print values before rendering
    print(f"📌 Debugging: {stock1_name} ({score1:.2f}) vs {stock2_name} ({score2:.2f})")
    print(f"Better Stock: {better_stock}, Score Difference: {score_difference}")

    # Generate a professional-looking conclusion
    conclusion_text = f'''
    <div style='border: 2px solid #4CAF50; padding: 15px; border-radius: 10px; background-color: #f9f9f9; color:black;'>
        <h3 style='color: #2E8B57;'>📊 Investment Conclusion</h3>
        <p style='font-size: 16px;'><b>{better_stock}</b> is the better investment based on below calculations using financial metrics.</p>
        <p style='font-size: 16px;'>The <b>MaxDelta</b> function assigns 1 score if higher value between the two stocks for that param else 0</p>
        <p style='font-size: 14px;'>The scoring model, considering Market Cap, P/E Ratio, EPS, and ROE (using scaling), resulted in:</p>
        <p style='font-size: 16px;'>Score = MaxDelta(Market Cap) + MaxDelta(1 / P/E Ratio) + MaxDelta(EPS) + MaxDelta(ROE) </p>
        <ul>
            <li><b>{stock1_name} Score:</b> {score1:.2f}</li>
            <li><b>{stock2_name} Score:</b> {score2:.2f}</li>
        </ul>
        <p style='font-size: 14px;'>The difference in score is <b>{score_difference:.2f}</b>, indicating {('a significant' if score_difference > 0.5 else 'no strong')} advantage.</p>
    </div>
    '''

    # Render it in Streamlit with HTML
    st.markdown(conclusion_text, unsafe_allow_html=True)


def main():
    # 🎨 Custom CSS for better UI
    st.markdown('''
        <style>
        .title {
            font-size: 24px;
            font-weight: bold;
            color: #004B87;
            text-align: center;
        }
        .subheader {
            font-size: 24px;
            font-weight: bold;
            color: #0077B6;
            margin-top: 20px;
        }
        .highlight {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
        }
        .ai-box {
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            background-color: #002B5B;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: justify;
        }
        .table-container {
            font-size: 16px;
            font-weight: bold;
            color: #333;
        }
        .table-container th {
            background-color: #004B87;
            color: white;
            font-size: 18px;
            padding: 10px;
        }
        .table-container td {
            background-color: #f8f9fa;
            padding: 8px;
            text-align: center;
        }
        .conclusion {
            font-size: 18px;
            font-weight: bold;
            color: #004B87;
            background-color: #E0F7FA;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            margin-top: 20px;
        }
        </style>
    ''', unsafe_allow_html=True)

    # 🏆 Title
    st.markdown('<p class="title" style="font-size:24px">📊 Stock Investment Analyzer</p>', unsafe_allow_html=True)

    # 🌍 Country Selection
    country = st.selectbox("🌎 Select Country:", list(COUNTRY_MAPPING.keys()),key="country")

    # 📌 Stock Selection
    stock_dict = get_top_stocks(country)
    stock_names = list(stock_dict.keys())

    col1, col2 = st.columns(2)
    with col1:
        stock1_name = st.selectbox("📈 Select First Stock:", options=stock_names,key="stock_1")
    with col2:
        stock2_name = st.selectbox("📉 Select Second Stock:", options=stock_names, key="stock_2")

    stock1 = stock_dict.get(stock1_name, "N/A")
    stock2 = stock_dict.get(stock2_name, "N/A")

    # ⏳ Investment Time Frame
    time_frame = st.selectbox("⏳ Select Investment Time Frame:", ["3mo", "6mo", "1y", "5y", "10y"],key="time")

    # 🚀 Analyze Button
    if st.button("🚀 Analyze"):
        if(stock1_name==stock2_name):
            st.error("Please select different stocks for comparison.")
            return
        st.markdown('<p class="subheader">📊 Fetching Stock Data...</p>', unsafe_allow_html=True)

        data1 = get_stock_data(stock1, time_frame)
        data2 = get_stock_data(stock2, time_frame)

        st.markdown('<p class="subheader">💰 100 INR/USD Investment Growth Over Time</p>', unsafe_allow_html=True)
        norm_data1 = calculate_investment_growth(data1)
        norm_data2 = calculate_investment_growth(data2)

        if norm_data1 is not None and norm_data2 is not None:
            st.line_chart(pd.DataFrame({stock1_name: norm_data1, stock2_name: norm_data2}))

        # 📊 Stock Comparison
        st.markdown('<p class="subheader">⚖️ Stock Comparison</p>', unsafe_allow_html=True)
        stock1_info = yf.Ticker(stock1).info
        stock2_info = yf.Ticker(stock2).info
        compare_stocks(stock1_name, stock1_info, stock2_name, stock2_info)


        #st.markdown('<p class="subheader">📑 Stock Attributes Comparison</p>', unsafe_allow_html=True)
        #st.markdown('<div class="table-container">', unsafe_allow_html=True)
        #st.write(comparison_table)  # Ensure this table's font is consistent
        #st.markdown('</div>', unsafe_allow_html=True)

        # 📌 Conclusion
        generate_conclusion(stock1_name, stock1_info, stock2_name, stock2_info)



        # 🤖 AI-Powered Insights
        st.markdown('<p class="subheader">🤖 AI-Powered Investment Insights</p>', unsafe_allow_html=True)
        with st.spinner("Fetching AI analysis..."):
            ai_analysis = get_llm_analysis(stock1_name, stock1_info, stock2_name, stock2_info)
            st.markdown(f'<p class="ai-box">{ai_analysis}</p>', unsafe_allow_html=True)



if __name__ == "__main__":
    main()
