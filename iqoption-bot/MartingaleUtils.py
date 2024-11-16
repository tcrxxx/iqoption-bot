from decimal import Decimal

def define_martingale_candle(candles, lost_score, lost_score_past=0):
    """
    Define a ação a ser realizada com base na análise das velas e no histórico de perdas.
    
    Args:
        candles (list): Lista de velas, onde cada vela é um dicionário com informações como 'close', 'high', 'low'.
        lost_score (int): Número de perdas consecutivas.
        lost_score_past (int): Número de perdas acumuladas anteriormente (opcional).

    Returns:
        dict: Dados analisados da última vela relevante, incluindo o tipo de ação sugerida.
    """
    # Exemplo de análise simples para identificar tendência
    if len(candles) < 2:
        return {"action": "hold", "reason": "Insufficient data"}

    last_candle = candles[-1]
    prev_candle = candles[-2]

    # Determinar tendência: Alta ou Baixa
    if last_candle["close"] > prev_candle["close"]:
        trend = "up"
    elif last_candle["close"] < prev_candle["close"]:
        trend = "down"
    else:
        trend = "neutral"

    return {
        "action": "call" if trend == "up" else "put" if trend == "down" else "hold",
        "lost_score": lost_score,
        "lost_score_past": lost_score_past,
        "trend": trend,
        "last_close": last_candle["close"],
        "prev_close": prev_candle["close"],
    }


def decide_action(martingale_data):
    """
    Decide a próxima ação a ser tomada com base nos dados de Martingale.

    Args:
        martingale_data (dict): Dados processados contendo ação sugerida e informações sobre a última vela.

    Returns:
        str: "call" ou "put", dependendo da decisão tomada.
    """
    action = martingale_data.get("action", "hold")
    if action == "hold":
        print(f"Nenhuma ação tomada. Motivo: {martingale_data.get('reason', 'Desconhecido')}")
        return "hold"

    print(f"Tendência identificada: {martingale_data['trend']}. Ação sugerida: {action}")
    return action
