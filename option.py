# Required Libraries
import pdb
import logging
import time
import datetime
import traceback
import requests  # For Telegram alerts
from Dhan_Tradehull import Tradehull
import pandas as pd
from datetime import datetime, timedelta
import talib
import xlwings as xw

# Dhan API Credentials
client_code = "1103012633"
token_id    = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzQyNzAxNzQzLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzAxMjYzMyJ9.dkWd2o0TwlqqruTomTSrnO3Jud4jt-Hvu8VBQJXieXraVoLa5ILIxX-9OxSVpwfGky418yq21xQyocXtgqaQhw"
tsl         = Tradehull(client_code,token_id)

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Open Excel Workbook
wb = xw.Book('Live option chain.xlsx')
sheet = wb.sheets['option_Chain']
filtered_sheet = wb.sheets['FilteredData']

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = "7652265017:AAHl_HN9-7C67vQjwSNt7L2MY2fL4wt4UiI"
TELEGRAM_CHAT_ID = "881317629"

def send_telegram_message(message):
    """Send alerts via Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.get(url, params=params)

# Trading Parameters
quantity = 75  # Number of contracts to trade
trade_active = False  # Flag to track active trade
entry_price = 0  # Store entry price of trade
stop_loss_price = 0  # Store stop-loss level


# # Fetch Nifty Historical Data
# def get_nifty_data():
#     try:
#         # Set date range for fetching historical data
#         # to_date = datetime.today().strftime('%Y-%m-%d')
#         # from_date = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')

#         # Fetch Nifty historical data (Make sure API parameters are correct)
#         nifty_chart = tsl.get_historical_data(tradingsymbol="NIFTY", exchange='INDEX', timeframe="5")  # Historical data)
#         #print (nifty_chart)

#         #filtered_sheet.range('A2').value = nifty_chart
        

#         # Ensure DataFrame is not empty
#         if nifty_chart is None or nifty_chart.empty:
#             print("⚠ Warning: No Nifty historical data received!")
#             return None

#         # Debugging: Print available data
#         #print("Nifty Data:\n", nifty_chart.tail())
#         #print("Number of rows:", len(nifty_chart))

#         # Calculate 9EMA & 15EMA
#         nifty_chart['9EMA'] = talib.EMA(nifty_chart['close'], timeperiod=9)
#         nifty_chart['15EMA'] =talib.EMA(nifty_chart['close'], timeperiod=15)
        
#         # Get latest and previous candle data
#         cc = nifty_chart.iloc[-2]
#         prev_cc = nifty_chart.iloc[-3]

#         return nifty_chart

#     except Exception as e:
#         print(f"Error fetching Nifty data: {e}")
#         return None





# # Function to Fetch Nifty Historical Data
# def get_nifty_data():
#     try:
#         # Fetch 5-minute historical data for NIFTY
#         nifty_chart = tsl.get_historical_data(tradingsymbol="NIFTY", exchange='INDEX', timeframe="5")
        
#         if nifty_chart is None or nifty_chart.empty:
#             print("⚠ Warning: No Nifty historical data received!")
#             return None
        
#         # Calculate 9-period and 15-period Exponential Moving Averages (EMA)
#         nifty_chart['9EMA'] = talib.EMA(nifty_chart['close'], timeperiod=9)
#         nifty_chart['15EMA'] = talib.EMA(nifty_chart['close'], timeperiod=15)
        
#         return nifty_chart
#     except Exception as e:
#         print(f"Error fetching Nifty data: {e}")
#         return None


# # while  True :
# #     nifty_chart = get_nifty_data()
# #     print(nifty_chart)
# #     filtered_sheet.range('A2').value = nifty_chart
# #     pdb.set_trace()



# # Fetch Option Chain Data & Trade Logic
# while True:
#     try:
#         # Get Nifty Data
#         nifty_chart = get_nifty_data()
#         if nifty_chart is None or len(nifty_chart) < 3:
#             print("⚠ Not enough data to check EMA crossover.")
#             continue

#         # Get latest and previous candle data
#         cc = nifty_chart.iloc[-2]
#         prev_cc = nifty_chart.iloc[-3]
#         positive_market = (prev_cc['EMA_9'] < prev_cc['EMA_15'] and cc['EMA_9'] > cc['EMA_15'])
#         negative_market = (prev_cc['EMA_9'] > prev_cc['EMA_15'] and cc['EMA_9'] < cc['EMA_15'])

#         option_chain = tsl.get_option_chain(Underlying="NIFTY", exchange="INDEX", expiry=0)


#         if nifty_chart is not None and len(nifty_chart) > 2:
            

#             # Check for Negative Market Condition
#             negative_market = (prev_cc['EMA_9'] > prev_cc['EMA_15'] and cc['EMA_9'] < cc['EMA_15'])

#             print(f"Positive Market: {positive_market}, Negative Market: {negative_market}")

#             # Fetch Option Chain Data
#             option_chain = tsl.get_option_chain(Underlying="NIFTY", exchange="INDEX", expiry=0)
#             if option_chain is not None and not option_chain.empty:
#                 print(f"Data received: {option_chain.shape}")

#                 # Select ATM Strike Price
#                 CE_symbol_name, PE_symbol_name, atm_strike = tsl.ATM_Strike_Selection(Underlying='NIFTY', Expiry=0)

#                 # Filter ATM Strike Data
#                 option_chain['Strike Price'] = option_chain['Strike Price'].astype(float)
#                 atm_data = option_chain[option_chain['Strike Price'] == atm_strike]

#                 if atm_data.empty:
#                     print("⚠ Warning: No ATM data found!")
#                     continue

#                 # Extract CE & PE LTP
#                 ce_ltp = atm_data['CE LTP'].values[0] if 'CE LTP' in atm_data.columns else None
#                 pe_ltp = atm_data['PE LTP'].values[0] if 'PE LTP' in atm_data.columns else None

#                 print(f"CE LTP: {ce_ltp}, PE LTP: {pe_ltp}")

#                 # Trading Conditions
#                 if positive_market and ce_ltp and not trade_active:
#                     quantity = quantity
#                     sl_price =( ce_ltp -5 )
#                     entry_orderid = tsl.order_placement(tradingsymbol=CE_symbol_name, exchange='NIFTY', quantity=quantity,
#                                                         price=0, trigger_price=0, order_type='MARKET',
#                                                         transaction_type='BUY', trade_type='MIS')
        
#                     sl_orderid = tsl.order_placement(tradingsymbol=CE_symbol_name, exchange='NIFTY', quantity=quantity,
#                                                      price=0, trigger_price=sl_price, order_type='STOPMARKET',
#                                                      transaction_type='SELL', trade_type='MIS')
#                     stop_loss_levels[name] = sl_price
#                     trade_active = 'yes'

#                     print(f"📈 Buying CALL Option: {CE_symbol_name} at {ce_ltp}")

#                 # Execute sell order if conditions met
#                 if negative_market and pe_ltp and not trade_active:
#                     quantity = quantity
#                     sl_price =( ce_ltp - 5 )
#                     entry_orderid = tsl.order_placement(tradingsymbol=PE_symbol_name, exchange='NIFTY', quantity=quantity,
#                                                         price=0, trigger_price=0, order_type='MARKET',
#                                                         transaction_type='BUY', trade_type='MIS')
        
#                     sl_orderid = tsl.order_placement(tradingsymbol=PE_symbol_name, exchange='NIFTY', quantity=quantity,
#                                                      price=0, trigger_price=sl_price, order_type='STOPMARKET',
#                                                      transaction_type='SELL', trade_type='MIS')
#                     stop_loss_levels[name] = sl_price
#                     trade_active = 'yes'
#                     print(f"📉 Buying PUT Option: {PE_symbol_name} at {pe_ltp}")



#                 else:
#                     print("⚠ No valid trading conditions met.")

#                 # Write to Excel
#                 sheet.api.Application.ScreenUpdating = False  # Pause updates for performance
#                 sheet.range('N2').value = atm_strike
#                 sheet.range('B1').value = CE_symbol_name
#                 sheet.range('B2').value = ce_ltp
#                 sheet.range('D1').value = PE_symbol_name
#                 sheet.range('D2').value = pe_ltp
#                 sheet.api.Application.ScreenUpdating = True  # Resume updates

#             else:
#                 print("⚠ Warning: Empty option_chain received.")

#         else:
#             print("⚠ Not enough data to check EMA crossover.")

#     except Exception as e:
#         print(f"Error: {e}")

#     time.sleep(30)  # Wait 30 seconds before fetching again


# Function to Fetch Nifty Historical Data
def get_nifty_data():
    try:
        print("Fetching Nifty data...")
        # Fetch 5-minute historical data for NIFTY
        nifty_chart = tsl.get_historical_data(tradingsymbol="NIFTY", exchange='INDEX', timeframe="5")
        
        if nifty_chart is None or nifty_chart.empty:
            print("⚠ Warning: No Nifty historical data received!")
            return None
        
        # Calculate 9-period and 15-period Exponential Moving Averages (EMA)
        nifty_chart['9EMA'] = talib.EMA(nifty_chart['close'], timeperiod=9)
        nifty_chart['15EMA'] = talib.EMA(nifty_chart['close'], timeperiod=15)
        nifty_chart['ATR'] = talib.ATR(nifty_chart['high'], nifty_chart['low'], nifty_chart['close'], timeperiod=14)


        print("Nifty data fetched successfully.")
        print(nifty_chart.tail())  # Debugging output
        return nifty_chart
    except Exception as e:
        print(f"Error fetching Nifty data: {e}")
        traceback.print_exc()
        return None

# Main Trading Loop
print("Entering main loop...")
while True:
    try:
        print("Loop iteration started...")
        # Fetch the latest Nifty data
        nifty_chart = get_nifty_data()
        if nifty_chart is None or len(nifty_chart) < 3:
            print("⚠ Not enough data to check EMA crossover.")
            continue

        # Get the latest two candles
        cc = nifty_chart.iloc[-2]  # Current candle
        prev_cc = nifty_chart.iloc[-3]  # Previous candle
        ema_difference = abs(cc['9EMA'] - cc['15EMA'])

        # Identify bullish and bearish crossover conditions
        positive_market = (prev_cc['9EMA'] < prev_cc['15EMA'] and cc['9EMA'] > cc['15EMA'])
        negative_market = (prev_cc['9EMA'] > prev_cc['15EMA'] and cc['9EMA'] < cc['15EMA'])
        sideways_market = (nifty_chart['ATR'].iloc[-1] < 20) or (ema_difference < 5)
        print(f"Positive Market: {positive_market}, Negative Market: {negative_market}, Sideways Market : {sideways_market}")

        # Fetch Option Chain Data
        option_chain = tsl.get_option_chain(Underlying="NIFTY", exchange="INDEX", expiry=0)
        if option_chain is None or option_chain.empty:
            print("⚠ Warning: Empty option_chain received.")
            continue

        # Select ATM (At The Money) Strike Prices
        CE_symbol_name, PE_symbol_name, atm_strike = tsl.ATM_Strike_Selection(Underlying='NIFTY', Expiry=0)
        option_chain['Strike Price'] = option_chain['Strike Price'].astype(float)
        atm_data = option_chain[option_chain['Strike Price'] == atm_strike]

        if atm_data.empty:
            print("⚠ Warning: No ATM data found!")
            continue

        # Get Last Traded Price (LTP) for Call & Put Options
        ce_ltp = atm_data['CE LTP'].values[0] if 'CE LTP' in atm_data.columns else None
        pe_ltp = atm_data['PE LTP'].values[0] if 'PE LTP' in atm_data.columns else None
        print(f"CE LTP: {ce_ltp}, PE LTP: {pe_ltp}")

        # Buy CALL option if bullish crossover detected
        if positive_market and ce_ltp and not trade_active and not sideways_market:
            entry_price = ce_ltp
            stop_loss_price = ce_ltp - 5  # Initial stop-loss level

            print(f"📈 Buying CALL Option: {CE_symbol_name} at {ce_ltp}")
            entry_orderid = tsl.order_placement(tradingsymbol=CE_symbol_name, exchange='NIFTY', quantity=quantity,
                                                price=0, trigger_price=0, order_type='MARKET',
                                                transaction_type='BUY', trade_type='MIS')
            sl_orderid = tsl.order_placement(tradingsymbol=CE_symbol_name, exchange='NIFTY', quantity=quantity,
                                             price=0, trigger_price=stop_loss_price, order_type='STOPMARKET',
                                             transaction_type='SELL', trade_type='MIS')
            trade_active = True
            send_telegram_message(f"✅ Market is Positive \n\nBUY ORDER: {CE_symbol_name}\n\nEntry: ₹{ce_ltp}\nSL: ₹{stop_loss_price}")

        # Buy PUT option if bearish crossover detected
        elif negative_market and pe_ltp and not trade_active and not sideways_market:
            entry_price = pe_ltp
            stop_loss_price = pe_ltp - 5  # Initial stop-loss level

            print(f"📉 Buying PUT Option: {PE_symbol_name} at {pe_ltp}")
            entry_orderid = tsl.order_placement(tradingsymbol=PE_symbol_name, exchange='NIFTY', quantity=quantity,
                                                price=0, trigger_price=0, order_type='MARKET',
                                                transaction_type='BUY', trade_type='MIS')
            sl_orderid = tsl.order_placement(tradingsymbol=PE_symbol_name, exchange='NIFTY', quantity=quantity,
                                             price=0, trigger_price=stop_loss_price, order_type='STOPMARKET',
                                             transaction_type='SELL', trade_type='MIS')
            trade_active = True
            send_telegram_message(f"✅ Market is Negative \n\nBUY ORDER: {PE_symbol_name}\n\nEntry: ₹{pe_ltp}\nSL: ₹{stop_loss_price}")

        elif sideways_market :
            print("⚠ No crossover detected and Market is also side ways, waiting for a signal...")

        # Manage Trailing Stop-Loss
        if trade_active:
            trade_type = "CALL" if positive_market else "PUT"  # Identify trade type
            current_ltp = ce_ltp if positive_market else pe_ltp  # Get current option price
            symbol_name = CE_symbol_name if positive_market else PE_symbol_name  # Get symbol name

            print(f"🔹 Active Trade: {trade_type} - {symbol_name}")
    
        # If price moves 5 points in profit, adjust stop-loss
            if current_ltp > entry_price + 5:
                new_sl_price = current_ltp - 5
                if new_sl_price > stop_loss_price:
                    stop_loss_price = new_sl_price  # Update stop-loss level
                    tsl.modify_order(order_id=sl_orderid, new_trigger_price=stop_loss_price)

                    print(f"🔄 Trailing Stop-Loss updated for {trade_type} to ₹{stop_loss_price}")
                    send_telegram_message(f"📢 🔄 Trailing Stop-Loss updated for {symbol_name} ({trade_type})\n\nNew SL: ₹{stop_loss_price}")


        time.sleep(15)  # Wait before next iteration

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        time.sleep(15)























###### BELOW CODE IS RUNNING FINE ##################


# while True:
#     try:
#         # Fetch option chain data
#         option_chain = tsl.get_option_chain(Underlying="NIFTY", exchange="INDEX", expiry=0)
#         CE_symbol_name, PE_symbol_name, atm_strike = tsl.ATM_Strike_Selection(Underlying='NIFTY', Expiry=0)
#         available_balance = tsl.get_balance()

#         if option_chain is not None and not option_chain.empty:
#             print(f"Data received: {option_chain.shape}")  # Debugging log
#             print("Available columns:", option_chain.columns)  # Check column names

#             # Ensure 'Strike Price' is in the DataFrame
#             if 'Strike Price' not in option_chain.columns:
#                 raise KeyError("Column 'Strike Price' not found in DataFrame!")

#             # Debug: Print available strike prices
#             print("ATM Strike:", atm_strike)
#             print("Available Strike Prices:", option_chain['Strike Price'].unique())

#             # Convert 'Strike Price' column to float for matching
#             option_chain['Strike Price'] = option_chain['Strike Price'].astype(float)
#             atm_strike = float(atm_strike)

#             # Filter using 'Strike Price'
#             atm_data = option_chain[option_chain['Strike Price'] == atm_strike]

#             # Debug: Check if filtering is working
#             print("Filtered ATM Data:\n", atm_data)

#             # Extract LTP
#             ce_ltp = atm_data['CE LTP'].values[0] if not atm_data.empty else None
#             pe_ltp = atm_data['PE LTP'].values[0] if not atm_data.empty else None

#             # Debug: Print extracted values
#             print(f"CE LTP: {ce_ltp}, PE LTP: {pe_ltp}")

#             # Write to Excel
#             sheet.api.Application.ScreenUpdating = False  # Pause updates for performance

#             # Write extracted values
#             sheet.range('N2').value = atm_strike
#             sheet.range('B1').value = CE_symbol_name  # Symbol name (for reference)
#             sheet.range('B2').value = ce_ltp  # Correct LTP extraction
#             sheet.range('D1').value = PE_symbol_name  # Symbol name (for reference)
#             sheet.range('D2').value = pe_ltp  # Correct LTP extraction
#             sheet.range('P2').value = available_balance
#             #**Clear previous data to avoid misalignment**
#             sheet.range('A4:AA500').clear_contents()

#             # **Write DataFrame to Excel**
#             sheet.range('A4').value = [option_chain.columns.tolist()]  # Column headers
#             sheet.range('A5').value = option_chain.values  # Data without index

#             sheet.api.Application.ScreenUpdating = True  # Resume updates

#         else:
#             print("Warning: Empty option_chain received.")

#     except KeyError as ke:
#         print(f"Column Error: {ke}")
#     except Exception as e:
#         print(f"Error: {e}")

#     time.sleep(30)  # Wait 30 seconds before fetching again


#######################################################################################################











































































# while True:
#     try:
#         # Fetch the option chain data
#         option_chain = tsl.get_option_chain(Underlying="NIFTY", exchange="INDEX", expiry=1)
#         CE_symbol_name, PE_symbol_name, atm_strike = tsl.ATM_Strike_Selection(Underlying='NIFTY', Expiry=1)

#         # Check if option_chain is valid
#         if option_chain is not None and not option_chain.empty:
#             print(f"Data received: {option_chain.shape}")  # Debugging log

            
#             option_chain_list = option_chain.fillna('').values.tolist() # Convert DataFrame to list of lists for faster Excel writing
#             sheet.api.Application.ScreenUpdating = False # Pause Excel updates for faster writing
#             sheet.range('A4').value = [option_chain.columns.tolist()] # Write column headers only once (if needed)
#             sheet.range('A5').value = option_chain_list # Write full DataFrame efficiently
#             sheet.range('N2').value = str(atm_strike) # Write ATM Strike separately
#             sheet.range('B2').value = str(CE_symbol_name)
#             sheet.range('D2').value = str(atm_strike)
#             sheet.api.Application.ScreenUpdating = True # Enable Excel updates after writing

#         else:
#             print("Warning: Empty option_chain received.")

#     except Exception as e:
#         print(f"Error: {e}")

#     time.sleep(30)  # Avoid spamming requests













# previous_df = None  # Store previous data to check for changes

# while True:
#     try:
#         # Fetch the option chain data
#         option_chain = tsl.get_option_chain(Underlying="NIFTY", exchange="INDEX", expiry=1)
#         CE_symbol_name, PE_symbol_name, atm_strike = tsl.ATM_Strike_Selection(Underlying='NIFTY', Expiry=1)

#         if option_chain is not None and not option_chain.empty:
#             option_chain = option_chain.fillna('')

#             # **Sort to maintain consistency**
#             if 'Strike Price' in option_chain.columns:
#                 option_chain = option_chain.sort_values(by='Strike Price', ascending=True)

#             if previous_df is not None and option_chain.equals(previous_df):
#                 print("No data change. Skipping Excel update.")
#             else:
#                 previous_df = option_chain.copy()

#                 # **Disable VBA events before writing**
#                 sheet.api.Application.EnableEvents = False  
#                 sheet.api.Application.ScreenUpdating = False  # Speed up updates

#                 # **Clear previous data to avoid misalignment**
#                 sheet.range('A4:AA500').clear_contents()

#                 # **Write DataFrame to Excel**
#                 sheet.range('A4').value = [option_chain.columns.tolist()]  # Column headers
#                 sheet.range('A5').value = option_chain.values  # Data without index
#                 sheet.range('C1').value = str(atm_strike)

#                 # **Re-enable VBA events**
#                 # sheet.api.Application.EnableEvents = True  
#                 # sheet.api.Application.ScreenUpdating = True  

#                 # **Manually trigger your VBA macro after writing data**
#                 #sheet.api.Application.Run("FindSortAndCopy")  # Replace with your actual macro name

#                 # **Force Excel to recalculate & refresh**
#                 sheet.api.Calculate()

#         else:
#             print("Warning: Empty option_chain received.")

#     except Exception as e:
#         print(f"Error: {e}")

#     time.sleep(20)  # 20-second delay to avoid conflicts