from nsepy import get_history
from datetime import date, datetime
import os
from tradingview_ta import TA_Handler, Interval, Exchange
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import colorama 
from colorama import Fore, Back, Style
colorama.init(autoreset=True)


a = """
 .d88888b.                             888    888888b.            
d88P" "Y88b                            888    888  "88b           
888     888                            888    888  .88P           
888     888 888  888  8888b.  88888b.  888888 8888888K.   .d88b.  
888     888 888  888     "88b 888 "88b 888    888  "Y88b d88""88b 
888 Y8b 888 888  888 .d888888 888  888 888    888    888 888  888 
Y88b.Y8b88P Y88b 888 888  888 888  888 Y88b.  888   d88P Y88..88P 
 "Y888888"   "Y88888 "Y888888 888  888  "Y888 8888888P"   "Y88P"  
       Y8b                                                        
                                                                  
                                                                  
"""

print(a)

Today = date.today()
y = Today.strftime("%Y")
m = Today.strftime("%m")
d = Today.strftime("%d")


last_order="sell"
sold_before = False
bought_before = False
current_price = 0
take_profit = 0.0
take_loss = 0.0


s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.maximize_window()
driver.get("https://in.tradingview.com/")
time.sleep(60)


#initiating tradingview handler to get the recomendation in 15 min interval
ssw = TA_Handler(
    symbol="INFY",
    screener="india",
    exchange="NSE",
    interval=Interval.INTERVAL_5_MINUTES
)
def countdown(t):

    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    if(current_time >= "09:20:00" and current_time < "15:20:00"):

        rec = ssw.get_analysis()
        RSI = rec.indicators["RSI"]
        EMA = rec.moving_averages["COMPUTE"]["EMA10"]
        print(Fore.YELLOW + "RSI:", RSI, Fore.YELLOW + "EMA:", EMA)


        if ( RSI >= 30 and RSI <= 69 and EMA == "BUY" ):   #industry standard rsi 30-70 bound technique
            if (last_order=="sell"):
                print(Fore.GREEN + "Buying 1 stock of Infosys")
                last_order="buy"
                print(last_order)
                print(sold_before)
                #buy 1 stock 
                driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div/div/div[1]/div[2]/div/div[2]/div[1]").click()
                driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div/div/div[1]/div[6]/button/div/span[2]").click()
                current_price = driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div/div/div[1]/div[2]/div/div[2]/div[2]/div").text
                print(current_price)
                take_profit = float(current_price) + 8
                take_loss = float(current_price) - 5
                while True:
                    print("Time left till next call - ")
                    countdown(int(5))
                    rec = ssw.get_analysis()
                    RSI = rec.indicators["RSI"]

                    EMA = rec.moving_averages["COMPUTE"]["EMA10"]
                    print(Fore.YELLOW +  "RSI:", RSI, Fore.YELLOW + "EMA:", EMA)
                    current_price = driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div/div/div[1]/div[2]/div/div[2]/div[2]/div").text
                    if((RSI >= 30 and EMA == "SELL") or (float(current_price) >= take_profit) or (float(current_price) <= take_loss)):
                        #sell the stock
                        print(Fore.RED + "Selling 1 stock of Infosys")
                        last_order="sell"
                        print(last_order)
                        #sell 1 stock 
                        driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div/div/div[1]/div[2]/div/div[1]").click()
                        time.sleep(2)
                        driver.find_element(By.XPATH,"//button[1]/div[1]/span[2]").click            ()
                        break
                    else:
                        print("no adjustment on pre-running algorithm required")
            else:
                print("last order not sold")
        elif( RSI >= 50 and EMA == "SELL" ):
            if ( last_order == "sell"):
                print(Fore.RED + "selling stock of INFOSYS")
                driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div/div/div[1]/div[2]/div/div[1]").click()
                time.sleep(2)
                driver.find_element(By.XPATH,"//button[1]/div[1]/span[2]").click            ()
                current_price = driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div/div/div[1]/div[2]/div/div[1]/div[2]/div").text
                print(current_price)
                take_profit = float(current_price) - 8
                take_loss = float(current_price) + 5
                while True:
                    print("Time left till next call - ")
                    countdown(int(5))
                    rec = ssw.get_analysis()
                    RSI = rec.indicators["RSI"]
                    EMA = rec.moving_averages["COMPUTE"]["EMA10"]
                    print("RSI:", RSI, "EMA:", EMA)
                    current_price = driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div/div/div[1]/div[2]/div/div[2]/div[2]/div").text
                    if((RSI <= 30 and EMA == "BUY") or ( float(current_price) <= take_profit) or (float(current_price) >= take_loss)):
                        #buy the stock
                        print(Fore.GREEN + "Buying stock")
                        driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div/div/div[1]/div[2]/div/div[2]/div[1]").click()
                        driver.find_element(By.XPATH,"//div[1]/div[1]/div[6]/button[1]/div[1]/span[2]").click()
                        break
                    else:
                        print("no adjustment required")

        else:
            print(Fore.LIGHTYELLOW_EX + "No applicable algorithm triggers, waiting...") 
          
    elif(current_time >= "15:20:00"):
        print("Closing for the day now")
        # #fetch open profit
        open_profit = driver.find_element(By.XPATH,"//div[4]/div[1]/div[1]/div[1]/div[2]/div[3]/div[1]").text
        # print(open_profit)
        # P = "1000"
        print("Calculating profit :",open_profit)
        break
    else:
        if(current_time >= "09:15:00" and current_time < "09:20:00"):
            print("Analysing market","\n\n")
        elif(current_time < "9:15:00"):
            print("Waiting for the market to open")
        else:
            print("No action required as of now")
        
