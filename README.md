# Dynamic-Stock-Analyzer
Choose the best stock to invest using LLM at any time, based on country.


This project compares two stocks based on historical data and financial metrics, providing insights through a Streamlit dashboard.

## Features
- Fetch stock data using Yahoo Finance API
- Compare stock price performance over different timeframes
- Display financial metrics comparison
- Interactive visualization with Streamlit

## Installation
```sh
pip install -r requirements.txt
```

## Usage
```sh
streamlit run app.py
```

## Files Structure
- `app.py` - Main Streamlit application
- `utils.py` - Helper functions for fetching data
- `requirements.txt` - Dependencies
- `README.md` - Project documentation
- `.gitignore` - Ignored files for Git


#### Setting Up Pyngrok API Key
To use `pyngrok`, follow these steps:
1. **Sign up on Ngrok**: Go to [Ngrok's website](https://ngrok.com/) and create an account.
2. **Get the API Key**: After signing in, navigate to the "Auth Token" section in the dashboard and copy it.

##### Setting Up Hugging Face API Key
To use Hugging Face models in this project, follow these steps:
1. **Create a Hugging Face Account**:  
   - Visit [Hugging Face](https://huggingface.co/) and sign up or log in.  
2. **Generate an API Key**:  
   - Go to **Settings → Access Tokens**.  
   - Click **New Token**, give it a name, and select **"Read" access**.  
   - Copy the generated API key.  
