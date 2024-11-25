import pprint
import CSVUtils
import config
import time
from decimal import Decimal
from operator import attrgetter
import PushbulletUtils
from collections import defaultdict
from iqoptionapi.stable_api import IQ_Option #Documentation: https://github.com/iqoptionapi/iqoptionapi/
import MartingaleUtils


iqoption = IQ_Option(config.IQOPTION_USER,config.IQOPTION_PASS)

#Configs Constants
ERROR_PASSWORD="""{"code":"invalid_credentials","message":"You entered the wrong credentials. Please check that the login/password is correct."}"""
BALANCE_TYPE="PRACTICE" #MODE="PRACTICE"/"REAL"/"TOURNAMENT
MFA_ENABLED=False
ACTIVES="EURUSD"
DIGITAL=True
DIGITAL_SUFFIX="-OTC"
ACTIVES_FINAL=ACTIVES + DIGITAL_SUFFIX if DIGITAL else ACTIVES
CANDLES_INTERVAL=300#120 
CANDLES_COUNT=222
CANDLES_SIZE="all" #size=[1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,"all"]
CANDLES_REAL_SIZE=600 #"all" #size:[1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,"all"]
CANDLES_MAX_BUFFER=50 # maxdict:set max buffer you want to save
DURATION=5#1#minute 1 or 5
AMOUNT=50
POLLING_TIME=3
USE_MAX_MIN=False

CHUNK_MARTIN=5

#Variables
win_score,lost_score, lost_limit,lost_score_past = 0,0,25,0
win_values,lost_values = 0,0
max_close_candle,min_close_candle = 0,0
loose_log_list = []
action="call"#put

print("******** Begin iqoption bot *********")
print("ACTIVES selected: ", ACTIVES_FINAL)
print("Balance type selected; ", BALANCE_TYPE)

print("Conecting...")
check,reason=iqoption.connect()

print('Reason:', reason)
print("Email:", iqoption.email)


PushbulletUtils.push_note_phone("Begin iqoption bot", " ACTIVES selected: " + ACTIVES_FINAL + " Balance type selected: " + BALANCE_TYPE)

def is_number(value):
    try:
        value = Decimal(value)
        return True
    except:
        return False

def try_bet(candles):

    global action, win_score, lost_score, lost_score_past, win_values, lost_values, max_close_candle, min_close_candle

    # Test logic
    # candles[-1]['close']=0.720685
    # last_bollinger_up=0.7206379734957176
    # last_bollinger_down=0.7203725265042824

    # while ((not(candles[-1]['close'] >= last_bollinger_up) and not(candles[-1]['close']  <= last_bollinger_down))):
        #    or not(not(candles[-1]['close'] >= max_close_candle) and not(candles[-1]['close']  <= min_close_candle))
    print("--------------------------------------------------------------------------------------------------------------")
    # candles = getCandles()
    
    chunk_last_action = MartingaleUtils.define_martingale_candle(candles,lost_score, lost_score_past) # candles[-5]
    lost_score_past += lost_score
    print(chunk_last_action)

    print("wins:" + str(win_score) + "(value:" + str(win_values) + ") - losts:" + str(lost_score) + " (value: " + str(lost_values) + ") - lost_limit:" + str(lost_limit))
    time.sleep(1)

    action = MartingaleUtils.decide_action(chunk_last_action)

    print("Action decide:" + action)

    if not DIGITAL:
        print("Buy Binary Option")
        _,id=iqoption.buy(AMOUNT,ACTIVES_FINAL,action,DURATION)
        print("Buy id: ", id)
        while iqoption.get_async_order(id)==None:
            pass
        order_data=iqoption.get_async_order(id)
        #print(iqoption.get_async_order(id))
        
        print("start check win please wait")
        print(iqoption.check_win_v2(id,POLLING_TIME))
        
    else:
        print("Buy Digital Option spot")
        _,id=iqoption.buy_digital_spot(ACTIVES_FINAL,AMOUNT,action,DURATION)
        print("Buy id: ", id)

        #TODO: if buy_id = {'message': 'active_closed: rejected by risks'} then error
        
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
                # bet_candle = iqoption.get_candles(ACTIVES_FINAL,CANDLES_INTERVAL,CANDLES_COUNT,time.time())
                bet_candle = getCandles()
                print("Final candle close:",bet_candle[-1])
                if float(win_money)>0:
                        win_values = win_values + float(win_money)
                        win_money=("%.2f" % (win_money))
                        print("you win",win_money,"money :D")
                        win_score = win_score + 1
                else:
                        print("you loose :(")
                        lost_score = lost_score + 1
                        lost_values = lost_values + float(win_money)
                        loose_log_list.append([candles[-1]['close'], max_close_candle,min_close_candle])
                break
            else:
                time.sleep(5)
        
        print("End of bet :)")

def getCandles():
    print("get candles")
    # candles = iqoption.get_candles(ACTIVES_FINAL,CANDLES_INTERVAL,CANDLES_COUNT,time.time())
    candles=iqoption.get_realtime_candles(ACTIVES_FINAL,CANDLES_REAL_SIZE)

    # pprint.pprint(candles)

    candles_list=[]
    if CANDLES_REAL_SIZE=="all":
        for id, info in candles.items():
            # print(id)
            for k in info:
                # print(k, info[k])
                # print(info[k]['close'])
                # print(info[k])
                if is_number(info['close']):
                    candles_list.append(info[k])
    else:
        for id, info in candles.items():
            # print(info)
            if is_number(info['close']):
                candles_list.append(info) 

    # return candles
    return candles_list

def getMinMaxClose(candles):
    max_close_candle = max(candles,key=lambda x:x['close'])['close']
    min_close_candle = min(candles,key=lambda x:x['close'])['close']
    return max_close_candle, min_close_candle

#MFA
if MFA_ENABLED:
     print("--------------------------------------------------------------------------------------------------------------")
     print("******** MFA Auth **********")
     code_sms = input("Enter the code received: ")
     status,reason = iqoption.connect_2fa(code_sms)
     print("Status:",status)
     print("Reason:", reason)
     print("--------------------------------------------------------------------------------------------------------------")

if check:
    print("--------------------------------------------------------------------------------------------------------------")
    print("********* Connected *********")
    print("Start your bot")
    print("Currency: ", iqoption.get_currency())
    iqoption.change_balance(BALANCE_TYPE)
    print("Balance Type:", BALANCE_TYPE)
    print("Balance:", iqoption.get_balance())
    print("wins:" + str(win_score) + "(value:" + str(win_values) + ") - losts:" + str(lost_score) + " (value: " + str(lost_values) + ") - lost_limit:" + str(lost_limit))
    print("Start Candles Stream...")
    iqoption.start_candles_stream(ACTIVES_FINAL,CANDLES_SIZE,CANDLES_MAX_BUFFER)
    print("--------------------------------------------------------------------------------------------------------------")
    
    candles = getCandles()

    # last_bollinger_up, last_bollinger_down = getBollingerBandsLimits(candles)
    # max_close_candle,min_close_candle = getMinMaxClose(candles)

    #if see this you can close network for test
    while lost_score < lost_limit:
        print("--------------------------------------------------------------------------------------------------------------")
        print("Try new bet!")
        print("wins:" + str(win_score) + "(value:" + str(win_values) + ") - losts:" + str(lost_score) + " (value: " + str(lost_values) + ") - lost_limit:" + str(lost_limit))
        try_bet(candles)
        print("--------------------------------------------------------------------------------------------------------------")

        if lost_score + 1 == lost_limit:
            PushbulletUtils.push_note_phone("Lost limit is near","Keep your yes open, because your bot is near to stop" + " - losts:" + str(lost_score) + " - lost_limit:" + str(lost_limit) + "wins:" + str(win_score) + "(value:" + str(win_values) + ") - losts:" + str(lost_score) + " (value: " + str(lost_values) + ") - lost_limit:" + str(lost_limit))


        if iqoption.check_connect()==False:#detect the websocket is close
            print("try reconnect")
            check,reason=iqoption.connect()
            if check:
                print("Reconnect successfully")
            else:
                if reason==ERROR_PASSWORD:
                    print("Error Password")
                else:
                    print("No Network")

    print("--------------------------------------------------------------------------------------------------------------")
    print("Lost limit reached -> losts:" + str(lost_score) + " - lost_limit:" + str(lost_limit))
    print("wins:" + str(win_score) + "(value:" + str(win_values) + ") - losts:" + str(lost_score) + " (value: " + str(lost_values) + ") - lost_limit:" + str(lost_limit))
    PushbulletUtils.push_note_phone("Lost limit reached -> losts:" + str(lost_score) + " - lost_limit:" + str(lost_limit), "wins:" + str(win_score) + "(value:" + str(win_values) + ") - losts:" + str(lost_score) + " (value: " + str(lost_values) + ") - lost_limit:" + str(lost_limit))
    print("Stop candles stream...")
    size=lost_score+win_score
    goal=ACTIVES
    iqoption.stop_candles_stream(goal,size)
    print("End of process!")

else:

    if reason=="[Errno -2] Name or service not known":
        print("No Network")
    elif reason==ERROR_PASSWORD:
        print("Error Password")
    else:
        print(reason)
