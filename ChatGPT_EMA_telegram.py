# Required Libraries
import pdb
import logging
import time
import datetime
import traceback
import requests  # For Telegram alerts
from Dhan_Tradehull import Tradehull
import pandas as pd
import talib
import xlwings as xw

# Dhan API Credentials
client_code = "1103012633"
token_id    = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzQyNzAxNzQzLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzAxMjYzMyJ9.dkWd2o0TwlqqruTomTSrnO3Jud4jt-Hvu8VBQJXieXraVoLa5ILIxX-9OxSVpwfGky418yq21xQyocXtgqaQhw"
tsl         = Tradehull(client_code,token_id)

# Set up logging
logging.basicConfig(filename='trade_bot.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = "7652265017:AAHl_HN9-7C67vQjwSNt7L2MY2fL4wt4UiI"
TELEGRAM_CHAT_ID = "881317629"

def send_telegram_message(message):
    """Send alerts via Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.get(url, params=params)

# Trading Settings
available_balance = tsl.get_balance()
leveraged_margin = available_balance * 5
max_trade = 5
per_trade_margin = leveraged_margin / max_trade
max_loss = (available_balance * 1) / 100 * -1  # 1% risk per trade


# Excel Setup
wb = xw.Book('ChatGPT_EMA_telegram.xlsx')
Live = wb.sheets['Live']
Orderbook = wb.sheets['Orderbook']
#Live.range('C1').value = available_balance


# Track Stop-Loss Levels
stop_loss_levels = {}  # Dictionary to store SL levels
active_trades = set()  # Track active trades
trade_data = {}  # Dictionary to store trade details

while True:
    try:
        # Fetch watchlist and latest LTP data
        watchlist = Live.range('A4').expand('down').value
        ltp_for_all_scripct = tsl.get_ltp_data(names=watchlist)

        for name in watchlist:
            try:
                # Fetch historical data for analysis
                ltp = ltp_for_all_scripct[name]
                chart = tsl.get_historical_data(tradingsymbol=name, exchange='NSE', timeframe="5")
                
                if len(chart) < 15:
                    continue
                
                # Calculate technical indicators
                chart['EMA_9']  = talib.EMA(chart['close'], timeperiod=9)
                chart['EMA_15'] = talib.EMA(chart['close'], timeperiod=15)
                chart['rsi']    = talib.RSI(chart['close'], timeperiod=14)

                # Get latest and previous candle data
                cc = chart.iloc[-2]
                prev_cc = chart.iloc[-3]
                
                row_no = str(watchlist.index(name) + 4)
                # Update live values in the sheet
                Live.range('B' + row_no).value = ltp
                Live.range('C' + row_no).value = round(cc['rsi'], 2)
                Live.range('D' + row_no).value = round(cc['EMA_9'], 2)
                Live.range('E' + row_no).value = round(cc['EMA_15'], 2)

                # Fetch stop-loss percentage from Excel
                Stop_loss_percent = Live.range('I1').value  

                # Determine buy/sell signals
                buy_signal = prev_cc['EMA_9'] < prev_cc['EMA_15'] and cc['EMA_9'] > cc['EMA_15']
                sell_signal = prev_cc['EMA_9'] > prev_cc['EMA_15'] and cc['EMA_9'] < cc['EMA_15']
                trade_active = Live.range('M' + row_no).value

                # Store previous buy/sell signals
                prev_buy = Live.range('F' + row_no).value
                prev_sell = Live.range('G' + row_no).value

                # Log buy/sell signals
                if buy_signal and prev_buy != "buy":
                    Live.range('F' + row_no).value = "buy"
                    Live.range('H' + row_no).value = ltp
                
                if sell_signal and prev_sell != "sell":
                    Live.range('G' + row_no).value = "sell"
                    Live.range('I' + row_no).value = ltp

                # Execute buy order if conditions met
                if buy_signal and not trade_active:
                    quantity = 1
                    sl_price = ltp * (1 - Stop_loss_percent / 100)
                    entry_orderid = tsl.order_placement(tradingsymbol=name, exchange='NSE', quantity=quantity,
                                                        price=0, trigger_price=0, order_type='MARKET',
                                                        transaction_type='BUY', trade_type='MIS')
                    sl_orderid = tsl.order_placement(tradingsymbol=name, exchange='NSE', quantity=quantity,
                                                     price=0, trigger_price=sl_price, order_type='STOPMARKET',
                                                     transaction_type='SELL', trade_type='MIS')
                    stop_loss_levels[name] = sl_price
                    Live.range('K' + row_no).value = entry_orderid
                    Live.range('L' + row_no).value = sl_orderid
                    Live.range('M' + row_no).value = "Yes"
                    send_telegram_message(f"✅ BUY ORDER: {name}\n\nEntry: ₹{ltp}\nSL: ₹{sl_price}")

                # Execute sell order if conditions met
                if sell_signal and not trade_active:
                    quantity = 1
                    sl_price = ltp * (1 + Stop_loss_percent / 100)
                    entry_orderid = tsl.order_placement(tradingsymbol=name, exchange='NSE', quantity=quantity,
                                                        price=0, trigger_price=0, order_type='MARKET',
                                                        transaction_type='SELL', trade_type='MIS')
                    sl_orderid = tsl.order_placement(tradingsymbol=name, exchange='NSE', quantity=quantity,
                                                     price=0, trigger_price=sl_price, order_type='STOPMARKET',
                                                     transaction_type='BUY', trade_type='MIS')
                    stop_loss_levels[name] = sl_price
                    Live.range('K' + row_no).value = entry_orderid
                    Live.range('L' + row_no).value = sl_orderid
                    Live.range('M' + row_no).value = "Yes"
                    send_telegram_message(f"🚨 SELL ORDER: {name}\n\nEntry: ₹{ltp}\nSL: ₹{sl_price}")
                
                # Update stop-loss only if in profit
                if trade_active == "Yes":
                    entry_price = Live.range('H' + row_no).value if Live.range('F' + row_no).value == "buy" else Live.range('I' + row_no).value
                    current_sl = stop_loss_levels.get(name,0 )

                    if Live.range('F' + row_no).value == "buy":
                        if ltp > entry_price:
                            new_sl = max(current_sl, ltp * (1 - Stop_loss_percent / 100))
                        else:
                            new_sl = current_sl
                    
                    elif Live.range('G' + row_no).value == "sell":
                        if ltp < entry_price:
                            new_sl = min(current_sl, ltp * (1 + Stop_loss_percent / 100))
                        else:
                            new_sl = current_sl

                    if new_sl != current_sl:
                        stop_loss_levels[name] = new_sl
                        Live.range('N' + row_no).value = stop_loss_levels[name]
                        if trade_active =="YES":
                            send_telegram_message(f"📢 STOP LOSS UPDATED: {name}\n\nNew SL: ₹{stop_loss_levels[name]}")
            
                # Check if stop-loss is hit
                if trade_active == "Yes" and name in stop_loss_levels:
                    if (Live.range('F' + row_no).value == "buy" and ltp <= stop_loss_levels[name]) or \
                        (Live.range('G' + row_no).value == "sell" and ltp >= stop_loss_levels[name]):
                        send_telegram_message(f"\U0001F525 STOP LOSS HIT: {name}\n\nSL: ₹{stop_loss_levels[name]}\nCurrent Price: ₹{ltp}")
                        trade_active = "No"  # Mark trade as inactive
                        stop_loss_levels.pop(name, None)  # Remove SL from tracking


            except Exception as e:
                error_message = f"🚨 ERROR processing {name}: {traceback.format_exc()}"
                logging.error(error_message)
                send_telegram_message(error_message)

        time.sleep(30)
    except Exception as e:
        logging.error("Critical Error: " + traceback.format_exc())
        send_telegram_message("🚨 Critical Error: " + traceback.format_exc())