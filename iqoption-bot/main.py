import bollingerBandsUtils
import config
import time
from collections import defaultdict
from iqoptionapi.stable_api import IQ_Option

error_password="""{"code":"invalid_credentials","message":"You entered the wrong credentials. Please check that the login/password is correct."}"""

iqoption = IQ_Option(config.IQOPTION_USER,config.IQOPTION_PASS)

balance_type="PRACTICE" #MODE="PRACTICE"/"REAL"/"TOURNAMENT
MFA_enabled=False
ACTIVES="EURUSD"
DIGITAL=True
DIGITAL_SUFFIX="-OTC"
ACTIVES_FINAL=ACTIVES + DIGITAL_SUFFIX if DIGITAL else ACTIVES
duration=1#minute 1 or 5
amount=1
action="call"#put
polling_time=3

print("******** Begin iqoption bot *********")
print("ACTIVES selected: ", ACTIVES_FINAL)
print("Balance type selected; ", balance_type)

print("Conecting...")
check,reason=iqoption.connect()

print('Reason:', reason)
print("Email:", iqoption.email)

#MFA
if MFA_enabled:
     print("******** MFA Auth **********")
     code_sms = input("Enter the code received: ")
     status,reason = iqoption.connect_2fa(code_sms)
     print("Status:",status)
     print("Reason:", reason)

if check:
    print("********* Connected *********")
    print("Start your bot")
    
    print("Currency: ", iqoption.get_currency())
    
    iqoption.change_balance(balance_type)
    
    print("get candles")
    candles = iqoption.get_candles(ACTIVES_FINAL,60,111,time.time())
    print(candles)

    print("Calculating Bollinger Bands")
    bollinger_up, bollinger_down = bollingerBandsUtils.get_bollinger_bands_candles(candles)

    last_bollinger_up, last_bollinger_down = bollinger_up.iloc[-1], bollinger_down.iloc[-1]
    print("Bollinger Bands - Last UP",last_bollinger_up)
    print("Bollinger Bands - Last DOWN",last_bollinger_down)

    print("Balance:", iqoption.get_balance())
    
    if not DIGITAL:
         print("Buy Binary Option")
         _,id=iqoption.buy(amount,ACTIVES_FINAL,action,duration)
         print("Buy id: ", id)
         while iqoption.get_async_order(id)==None:
             pass
         order_data=iqoption.get_async_order(id)
         #print(iqoption.get_async_order(id))
         
         print("start check win please wait")
         print(iqoption.check_win_v2(id,polling_time))
         
    else:
         print("Buy Digital Option spot")
         _,id=iqoption.buy_digital_spot(ACTIVES_FINAL,amount,action,duration)
         print("Buy id: ", id)
         
         while iqoption.get_async_order(id)==None:
             pass
         time.sleep(5)
         order_data=iqoption.get_async_order(id)
         #print(iqoption.get_async_order(id))
         
         print("start check win please wait")
         while True:
              print("wait...")
              check_close,win_money=iqoption.check_win_digital_v2(id)
              
              if check_close:
                   if float(win_money)>0:
                        win_money=("%.2f" % (win_money))
                        print("you win",win_money,"money :D")
                   else:
                        print("you loose :(")
                   break
              else:
                  time.sleep(5)
         
         print("End of process :)")

    #if see this you can close network for test
    while True:
        if iqoption.check_connect()==False:#detect the websocket is close
            print("try reconnect")
            check,reason=iqoption.connect()
            if check:
                print("Reconnect successfully")
            else:
                if reason==error_password:
                    print("Error Password")
                else:
                    print("No Network")

else:

    if reason=="[Errno -2] Name or service not known":
        print("No Network")
    elif reason==error_password:
        print("Error Password")
    else:
        print(reason)
