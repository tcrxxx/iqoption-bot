from decimal import Decimal

def define_martingale_candle(candles, lost_score, is_lost_past):
    """
    Define a ação a ser realizada com base na análise das velas e no histórico de perdas.
    
    Args:
        candles (list): Lista de velas, onde cada vela é um dicionário com informações como 'close', 'high', 'low'.
        lost_score (int): Número de perdas consecutivas.
        is_lost_past (boolean): Foi perda no round anterior

    Returns:
        dict: Dados analisados da última vela relevante, incluindo o tipo de ação sugerida.
    """
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
        "is_lost_past": is_lost_past,
        "trend": trend,
        "last_close": last_candle["close"],
        "prev_close": prev_candle["close"],
    }


def decide_action(martingale_data):
    """
    Decide a próxima ação a ser tomada com base nos dados de Martingale e no histórico de perdas.

    Args:
        martingale_data (dict): Dados processados contendo ação sugerida e informações sobre a última vela.

    Returns:
        str: "call", "put" ou "hold", dependendo da decisão tomada.
    """
    action = martingale_data.get("action", "hold")
    trend = martingale_data.get("trend", "neutral")
    lost_score = martingale_data.get("lost_score", 0)
    is_lost_past = martingale_data.get("is_lost_past", 0)

    if action == "hold":
        print(f"Nenhuma ação tomada. Motivo: {martingale_data.get('reason', 'Desconhecido')}")
        return "hold"

    # Se a última rodada foi perda, aplica lógica de Martingale
    if is_lost_past:
        print(f"Última rodada foi uma perda. Ajustando estratégia...")
        if trend == "up":
            next_action = "put"
        elif trend == "down":
            next_action = "call"
        else:
            next_action = action  # Mantém a decisão anterior como fallback
    else:
        # Caso contrário, segue a ação sugerida normalmente
        next_action = action

    print(
        f"Histórico de perdas: Atual: {lost_score}, Anterior foi perda? {is_lost_past}. "
        f"Tendência atual: {trend}. Próxima ação: {next_action}"
    )
    return next_action
