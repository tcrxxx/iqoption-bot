import time
from decimal import Decimal
from collections import defaultdict
from iqoptionapi.stable_api import IQ_Option  # Documentation: https://github.com/iqoptionapi/iqoptionapi/
import config
import MartingaleUtils
import PushbulletUtils

# Configurações
ERROR_PASSWORD = '{"code":"invalid_credentials","message":"You entered the wrong credentials."}'
BALANCE_TYPE = "PRACTICE"  # Modos disponíveis: "PRACTICE", "REAL", "TOURNAMENT"
ACTIVES = "EURUSD"
DIGITAL = True
# CANDLES_INTERVAL = 300
CANDLES_COUNT = 222
CANDLES_REAL_SIZE = 300
CANDLES_MAX_BUFFER = 50
DURATION = 1
AMOUNT = 50
POLLING_TIME = 3
LOST_LIMIT = 25
MFA_ENABLED = False

ACTIVES_FINAL = f"{ACTIVES}-OTC" if DIGITAL else ACTIVES

# Variáveis globais
win_score, lost_score, win_values, lost_values = 0, 0, 0, 0
action = "call"
loose_log_list = []

# Funções auxiliares
def is_number(value):
    """Verifica se o valor pode ser convertido para Decimal."""
    try:
        Decimal(value)
        return True
    except (ValueError, TypeError):
        return False

def get_candles():
    """Obtém as velas do mercado."""
    candles = iqoption.get_realtime_candles(ACTIVES_FINAL, CANDLES_REAL_SIZE)
    return [
        info
        for info in candles.values()
        if is_number(info.get("close"))
    ]

def try_bet(candles):
    """Executa uma tentativa de aposta baseada nos dados de velas."""
    global action, win_score, lost_score, win_values, lost_values

    print("Iniciando nova tentativa de aposta...")
    chunk_last_action = MartingaleUtils.define_martingale_candle(candles, lost_score)
    action = MartingaleUtils.decide_action(chunk_last_action)
    print(f"Ação decidida: {action}")

    if action=="hold":
        print("Ação indicada hold. Aguardando o mercado para iniciar nova ação.")
        time.sleep(5)
        return

    if not DIGITAL:
        print("Comprando opção binária comum")
        _,id=iqoption.buy(AMOUNT,ACTIVES_FINAL,action,DURATION)
        print("Compra com id: ", id)
        while iqoption.get_async_order(id)==None:
            pass
        order_data=iqoption.get_async_order(id)
        #print(iqoption.get_async_order(id))
        
        print("Iniciando a checagam de vitória...")
        print(iqoption.check_win_v2(id,POLLING_TIME))
        
    else:
        print("Comprando opção digital")
        _,id=iqoption.buy_digital_spot(ACTIVES_FINAL,AMOUNT,action,DURATION)
        print("Compra com id: ", id)

        #TODO: if buy_id = {'message': 'active_closed: rejected by risks'} then error
        
        while iqoption.get_async_order(id)==None:
            pass
        time.sleep(5)
        order_data=iqoption.get_async_order(id)
        #print(iqoption.get_async_order(id))
        
        print("Iniciando a verificação de ganho...")
        while True:
            print("aguarde...")
            check_close,win_money=iqoption.check_win_digital_v2(id)
            
            if check_close:
                # bet_candle = iqoption.get_candles(ACTIVES_FINAL,CANDLES_INTERVAL,CANDLES_COUNT,time.time())
                bet_candle = get_candles()
                print("Final candle close:",bet_candle[-1])
                if float(win_money)>0:
                        win_values = win_values + float(win_money)
                        win_money=("%.2f" % (win_money))
                        print("Você ganhou ",win_money," money :D")
                        win_score = win_score + 1
                else:
                        print("Você perdeu :(")
                        lost_score = lost_score + 1
                        lost_values = lost_values + float(win_money)
                        loose_log_list.append([candles[-1]['close'], candles[-1]['max'],candles[-1]['min']])
                break
            else:
                time.sleep(5)
        
        print("Fim da aposta :)")

# Conexão com a IQ Option
iqoption = IQ_Option(config.IQOPTION_USER, config.IQOPTION_PASS)
print("Conectando à IQ Option...")
check, reason = iqoption.connect()

if not check:
    print(f"Erro de conexão: {reason}")
    exit()

# Autenticação 2FA
if MFA_ENABLED:
    code_sms = input("Digite o código de autenticação: ")
    status, reason = iqoption.connect_2fa(code_sms)
    if not status:
        print(f"Erro na autenticação 2FA: {reason}")
        exit()

# Configuração inicial
iqoption.change_balance(BALANCE_TYPE)
iqoption.start_candles_stream(ACTIVES_FINAL, CANDLES_REAL_SIZE, CANDLES_MAX_BUFFER)
PushbulletUtils.push_note_phone("Bot iniciado", f"Ativo: {ACTIVES_FINAL}, Tipo de saldo: {BALANCE_TYPE}")

print(f"Saldo inicial: {iqoption.get_balance()}")

# Loop principal
while lost_score < LOST_LIMIT:
    print(f"Placar: Vitórias: {win_score}, Derrotas: {lost_score}")
    candles = get_candles()
    try_bet(candles)

print("Limite de perdas atingido. Finalizando bot.")
PushbulletUtils.push_note_phone("Bot finalizado", f"Vitórias: {win_score}, Derrotas: {lost_score}")
iqoption.stop_candles_stream(ACTIVES_FINAL)
