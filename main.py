import requests
import time
from datetime import datetime

TOKEN = "8650440936:AAFf95sqPgbq0Dzw4_SA_mNYrDUF0dH7eo4"
CHAT = "6167991088"

SEUIL_HAUSSE_PRIX = 3.0
INTERVALLE_SCAN = 30
BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

donnees_precedentes = {}
alertes_envoyees = {}

def envoyer_alerte(message):
    url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    payload = {
        "chat_id":CHAT,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Erreur envoi Telegram : " + str(e))

def scanner():
    global donnees_precedentes, alertes_envoyees
    try:
        data = requests.get(BINANCE_URL, timeout=10).json()
        paires = [d for d in data if d["symbol"].endswith("USDT")]
        for crypto in paires:
            symbol = crypto["symbol"]
            prix = float(crypto["lastPrice"])
            if symbol in donnees_precedentes and donnees_precedentes[symbol] > 0:
                hausse = ((prix - donnees_precedentes[symbol]) / donnees_precedentes[symbol]) * 100
                if hausse >= SEUIL_HAUSSE_PRIX:
                    maintenant = time.time()
                    if maintenant - alertes_envoyees.get(symbol, 0) > 300:
                        message = "Pompe detectee : " + symbol + " +" + str(round(hausse, 2)) + "% en " + str(INTERVALLE_SCAN) + "s"
                        envoyer_alerte(message)
                        alertes_envoyees[symbol] = maintenant
                        print("Alerte : " + symbol + " +" + str(round(hausse, 2)) + "%")
            donnees_precedentes[symbol] = prix
    except Exception as e:
        print("Erreur scanner : " + str(e))

envoyer_alerte("Scanner Crypto demarre !")
print("Scanner demarre !")
while True:
    scanner()
    print("Scan... " + datetime.now().strftime("%H:%M:%S"))
    time.sleep(INTERVALLE_SCAN)
