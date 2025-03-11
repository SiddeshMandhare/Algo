import pdb
import logging
import time
import datetime
import traceback
import requests  # For Telegram alerts
from Dhan_Tradehull import Tradehull
import pandas as pd
import talib
from datetime import datetime, time  # Handles time comparison
import time as t  # Renaming time module to avoid conflict


# Dhan API Credentials
client_code = "1103012633"
token_id    = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzQyNzAxNzQzLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzAxMjYzMyJ9.dkWd2o0TwlqqruTomTSrnO3Jud4jt-Hvu8VBQJXieXraVoLa5ILIxX-9OxSVpwfGky418yq21xQyocXtgqaQhw"
tsl         = Tradehull(client_code,token_id)

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = "7652265017:AAHl_HN9-7C67vQjwSNt7L2MY2fL4wt4UiI"
TELEGRAM_CHAT_ID = "881317629"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.get(url, params=params)

# Trading Parameters
quantity = 75  # Number of contracts to trade
trade_active = False  # Flag to track active trade
entry_price = 0  # Store entry price of trade
stop_loss_price = 0  # Store stop-loss level

# Trading Settings
available_balance = tsl.get_balance()
leveraged_margin = available_balance * 5
max_trade = 5
per_trade_margin = leveraged_margin / max_trade
max_loss = (available_balance * 1) / 100 * -1  # 1% risk per trade


# Data Storage
option_chain_df = pd.DataFrame()

def get_nifty_data():
    try:
        print("Fetching Nifty data...")
        nifty_chart = tsl.get_historical_data(tradingsymbol="NIFTY", exchange='INDEX', timeframe="5")
        
        if nifty_chart is None or nifty_chart.empty:
            print("⚠ Warning: No Nifty historical data received!")
            return None
        
        nifty_chart['9EMA'] = talib.EMA(nifty_chart['close'], timeperiod=9)
        nifty_chart['15EMA'] = talib.EMA(nifty_chart['close'], timeperiod=15)
        nifty_chart['ATR'] = talib.ATR(nifty_chart['high'], nifty_chart['low'], nifty_chart['close'], timeperiod=14)

        print("Nifty data fetched successfully.")
        print(nifty_chart.tail())
        return nifty_chart
    except Exception as e:
        print(f"Error fetching Nifty data: {e}")
        traceback.print_exc()
        return None


# Main Trading Loop
print("Entering main loop...")


while True:
    current_time = datetime.now().time()

    if current_time < time(3, 21):
        print("Wait for market to open", current_time)
        t.sleep(10)  # ✅ Using t.sleep() to avoid conflict
        continue

    if current_time > time(3, 22):
        print("Market is over, Bye Bye! See you tomorrow", current_time)
        break

    print("Algo is working", current_time)

    while True:
        current_time = datetime.now().time()

        if current_time > time(3, 22):
            print("❌ Market is over, Bye Bye! See you tomorrow.")
            break

        t.sleep(10)  # ✅ Using t.sleep()
        try:
            print("Loop iteration started...")
            nifty_chart = get_nifty_data()
            if nifty_chart is None or len(nifty_chart) < 3:
                print("⚠ Not enough data to check EMA crossover.")
                continue

            cc = nifty_chart.iloc[-2]
            prev_cc = nifty_chart.iloc[-3]
            ema_difference = abs(cc['9EMA'] - cc['15EMA'])

            positive_market = (prev_cc['9EMA'] < prev_cc['15EMA'] and cc['9EMA'] > cc['15EMA'])
            negative_market = (prev_cc['9EMA'] > prev_cc['15EMA'] and cc['9EMA'] < cc['15EMA'])
            sideways_market = (nifty_chart['ATR'].iloc[-1] < 20) or (ema_difference < 5)
            print(f"Positive Market: {positive_market}, Negative Market: {negative_market}, Sideways Market : {sideways_market}")

            option_chain = tsl.get_option_chain(Underlying="NIFTY", exchange="INDEX", expiry=0)
            if option_chain is None or option_chain.empty:
                print("⚠ Warning: Empty option_chain received.")
                continue

            option_chain_df = option_chain  # Store in DataFrame
            
            CE_symbol_name, PE_symbol_name, atm_strike = tsl.ATM_Strike_Selection(Underlying='NIFTY', Expiry=0)
            option_chain['Strike Price'] = option_chain['Strike Price'].astype(float)
            atm_data = option_chain[option_chain['Strike Price'] == atm_strike]

            if atm_data.empty:
                print("⚠ Warning: No ATM data found!")
                continue

            ce_ltp = atm_data['CE LTP'].values[0] if 'CE LTP' in atm_data.columns else None
            pe_ltp = atm_data['PE LTP'].values[0] if 'PE LTP' in atm_data.columns else None
            print(f"CE LTP: {ce_ltp}, PE LTP: {pe_ltp}")

            if positive_market and ce_ltp and not trade_active and not sideways_market:
                entry_price = ce_ltp
                stop_loss_price = ce_ltp - 5
                print(f"📈 Buying CALL Option: {CE_symbol_name} at {ce_ltp}")
                entry_orderid=tsl.order_placement(CE_symbol_name, 'NIFTY', quantity, 0, 0, 'MARKET', 'BUY', 'MIS')
                sl_orderid = tsl.order_placement(CE_symbol_name, 'NIFTY', quantity, 0, stop_loss_price, 'STOPMARKET', 'SELL', 'MIS')
                trade_active = True
                send_telegram_message(f"✅ Market is Positive \n\nBUY ORDER: {CE_symbol_name}\n\nEntry: ₹{ce_ltp}\nSL: ₹{stop_loss_price}")

            elif negative_market and pe_ltp and not trade_active and not sideways_market:
                entry_price = pe_ltp
                stop_loss_price = pe_ltp - 5
                print(f"📉 Buying PUT Option: {PE_symbol_name} at {pe_ltp}")
                entry_orderid = tsl.order_placement(PE_symbol_name, 'NIFTY', quantity, 0, 0, 'MARKET', 'BUY', 'MIS')
                sl_orderid = tsl.order_placement(PE_symbol_name, 'NIFTY', quantity, 0, stop_loss_price, 'STOPMARKET', 'SELL', 'MIS')
                trade_active = True
                send_telegram_message(f"✅ Market is Negative \n\nBUY ORDER: {PE_symbol_name}\n\nEntry: ₹{pe_ltp}\nSL: ₹{stop_loss_price}")

            elif sideways_market:
                print("⚠ No crossover detected and Market is sideways, waiting for a signal...")

            if trade_active:
                trade_type = "CALL" if positive_market else "PUT"
                current_ltp = ce_ltp if positive_market else pe_ltp
                symbol_name = CE_symbol_name if positive_market else PE_symbol_name
                print(f"🔹 Active Trade: {trade_type} - {symbol_name}")
        
                if current_ltp > entry_price + 5:
                    new_sl_price = current_ltp - 5
                    if new_sl_price > stop_loss_price:
                        stop_loss_price = new_sl_price
                        tsl.modify_order(order_id=sl_orderid, new_trigger_price=stop_loss_price)
                        print(f"🔄 Trailing Stop-Loss updated for {trade_type} to ₹{stop_loss_price}")
                        send_telegram_message(f"📢 🔄 Trailing Stop-Loss updated for {symbol_name} ({trade_type})\n\nNew SL: ₹{stop_loss_price}")

            t.sleep(15)
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            t.sleep(15)
