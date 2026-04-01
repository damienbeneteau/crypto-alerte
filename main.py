import requests
import time
from datetime import datetime
import os

# ─── Configuration ────────────────────────────────────────────────
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT = "6167991088"
SEUIL_HAUSSE_PRIX = 0.1    # % de hausse pour déclencher une alerte
INTERVALLE_SCAN = 30        # secondes entre chaque scan
COOLDOWN_ALERTE = 300       # secondes minimum entre deux alertes pour un même symbole
BINANCE_URL = "https://api.binance.us/api/v3/ticker/24hr"

# ─── État global ──────────────────────────────────────────────────
donnees_precedentes = {}    # { symbol: prix_précédent }
alertes_envoyees = {}       # { symbol: timestamp_dernière_alerte }

# ─── Vérification du token au démarrage ──────────────────────────
if not TOKEN:
    raise EnvironmentError("TELEGRAM_TOKEN non défini dans les variables d'environnement.")

def log(msg):
    """Affiche un message avec horodatage."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def envoyer_alerte(message):
    """Envoie un message Telegram au chat configuré."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            log(f"Telegram HTTP {r.status_code} : {r.text}")
    except Exception as e:
        log(f"Erreur envoi Telegram : {e}")

def scanner():
    """Récupère les prix Binance et envoie une alerte si hausse >= seuil."""
    global donnees_precedentes, alertes_envoyees

    try:
        response = requests.get(BINANCE_URL, timeout=10)
        response.raise_for_status()  # Lève une exception si HTTP 4xx/5xx
        data = response.json()

        if not isinstance(data, list):
            log("Réponse Binance inattendue (pas une liste).")
            return

        paires_usdt = [
            d for d in data
            if isinstance(d, dict) and d.get("symbol", "").endswith("USDT")
        ]

        maintenant = time.time()

        for crypto in paires_usdt:
            symbol = crypto.get("symbol")
            try:
                prix = float(crypto["lastPrice"])
            except (KeyError, ValueError):
                continue  # Donnée malformée, on passe

            prix_precedent = donnees_precedentes.get(symbol)

            # Premier cycle : on mémorise sans comparer
            if prix_precedent is None or prix_precedent == 0:
                donnees_precedentes[symbol] = prix
                continue

            hausse = ((prix - prix_precedent) / prix_precedent) * 100

            if hausse >= SEUIL_HAUSSE_PRIX:
                derniere_alerte = alertes_envoyees.get(symbol, 0)

                if maintenant - derniere_alerte > COOLDOWN_ALERTE:
                    message = (
                        f"🚀 <b>Pompe détectée : {symbol}</b>\n"
                        f"+{round(hausse, 2)}% en {INTERVALLE_SCAN}s\n"
                        f"Prix : {prix} USDT"
                    )
                    envoyer_alerte(message)
                    alertes_envoyees[symbol] = maintenant
                    log(f"Alerte envoyée : {symbol} +{round(hausse, 2)}%")

            donnees_precedentes[symbol] = prix

    except requests.exceptions.RequestException as e:
        log(f"Erreur réseau Binance : {e}")
    except Exception as e:
        log(f"Erreur scanner : {e}")

# ─── Boucle principale ────────────────────────────────────────────
if __name__ == "__main__":
    log("Bot de détection de pompes démarré.")
    envoyer_alerte("✅ Bot démarré et connecté à Telegram.")
    while True:
        scanner()
        time.sleep(INTERVALLE_SCAN)
