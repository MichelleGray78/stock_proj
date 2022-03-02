import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client
import datetime

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

load_dotenv()

# Getting json stock data
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
api_key = os.getenv("API_KEY")

parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": api_key
}

response = requests.get(url=STOCK_ENDPOINT, params=parameters)
response.raise_for_status()
data = response.json()

# Getting json news data
news_api_key = os.getenv("NEWS_API_KEY")
news_params = {
    "q": COMPANY_NAME,
    "apiKey": news_api_key,
}
news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
news_response.raise_for_status()
news_data = news_response.json()["articles"]

# Twilio
twilio_api_key = os.getenv("TWILIO_API_KEY")
account_sid = os.getenv("ACCOUNT_SID")
auth_tok = os.getenv("AUTH_TOKEN")
phone_no = os.getenv("PHONE_NO")
my_phone_no = os.getenv("MY_PHONE_NO")

## STEP 1: Use https://www.alphavantage.co/documentation/#daily
# When stock price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
# Getting dates
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
day_before_yest = yesterday - datetime.timedelta(days=1)

# Getting yesterdays and day befores stock prices
yest_close_stock = data["Time Series (Daily)"][f"{yesterday}"]["4. close"]
day_before_close_stock = data["Time Series (Daily)"][f"{day_before_yest}"]["4. close"]
print(f"yest close = {yest_close_stock}, day before close = {day_before_close_stock}")

#TODO 3. - Find the positive difference between 1 and 2. e.g. 40 - 20 = -20, but the positive difference is 20. Hint: https://www.w3schools.com/python/ref_func_abs.asp
pos_diff = float(yest_close_stock) - float(day_before_close_stock)
up_down = None
if pos_diff > 0:
    up_down = "🔺"
else:
    up_down = "🔻"
    
# Percentage
percentage_gain = round((pos_diff/float(day_before_close_stock)) * 100)

#TODO 5. - If TODO4 percentage is greater than 5 then print("Get News").
if abs(percentage_gain) > 5:
    three_articles = news_data[:3]
    formatted_articles = [f"{STOCK_NAME}: {up_down}{percentage_gain}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]
    for item in formatted_articles:
        client = Client(account_sid, auth_tok)
        message = client.messages \
                        .create(
                            body=item,
                            from_= phone_no,
                            to=my_phone_no
                            )


"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

