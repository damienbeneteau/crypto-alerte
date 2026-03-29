import requests
import time
from datetime import datetime

# ============================================

# 🔧 CONFIGURATION - REMPLIS CES 2 VALEURS

# ============================================

import os
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN"

TELEGRAM_CHAT_ID = “6167991088”   # Ton Chat ID

# ============================================

# ⚙️ PARAMÈTRES DE DÉTECTION

# ============================================

SEUIL_HAUSSE_PRIX = 3.0      # % de hausse minimum pour alerter
SEUIL_HAUSSE_VOLUME = 2.0    # x fois le volume normal
INTERVALLE_SCAN = 30         # secondes entre chaque scan
BINANCE_URL = “https://api.binance.com/api/v3/ticker/24hr”

# ============================================

# 📦 STOCKAGE DES DONNÉES PRÉCÉDENTES

# ============================================

donnees_precedentes = {}
alertes_envoyees = {}  # Évite les alertes en double

def envoyer_alerte(message):
“”“Envoie une alerte sur Telegram”””
url = f”https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage”
payload = {
“chat_id”: TELEGRAM_CHAT_ID,
“text”: message,
“parse_mode”: “HTML”
}
try:
requests.post(url, json=payload, timeout=10)
except Exception as e:
print(f”Erreur envoi Telegram : {e}”)

def recuperer_donnees_binance():
“”“Récupère toutes les paires USDT sur Binance”””
try:
response = requests.get(BINANCE_URL, timeout=10)
data = response.json()
# Filtre uniquement les paires USDT
paires_usdt = [d for d in data if d[‘symbol’].endswith(‘USDT’)]
return paires_usdt
except Exception as e:
print(f”Erreur Binance API : {e}”)
return []

def analyser_cryptos(donnees_actuelles):
“”“Analyse chaque crypto et détecte les anomalies”””
global donnees_precedentes, alertes_envoyees

```
for crypto in donnees_actuelles:
    symbol = crypto['symbol']
    prix_actuel = float(crypto['lastPrice'])
    volume_actuel = float(crypto['volume'])
    hausse_24h = float(crypto['priceChangePercent'])

    # Si on a des données précédentes pour cette crypto
    if symbol in donnees_precedentes:
        prix_precedent = donnees_precedentes[symbol]['prix']
        volume_precedent = donnees_precedentes[symbol]['volume']

        # Calcul de la hausse depuis le dernier scan
        if prix_precedent > 0:
            hausse_recente = ((prix_actuel - prix_precedent) / prix_precedent) * 100
        else:
            hausse_recente = 0

        # Calcul de l'explosion du volume
        if volume_precedent > 0:
            ratio_volume = volume_actuel / volume_precedent
        else:
            ratio_volume = 1

        # ✅ Détection d'une pompe
        if hausse_recente >= SEUIL_HAUSSE_PRIX and ratio_volume >= SEUIL_HAUSSE_VOLUME:

            # Évite d'envoyer 2 alertes pour la même crypto en moins de 5 min
            maintenant = time.time()
            derniere_alerte = alertes_envoyees.get(symbol, 0)
            if maintenant - derniere_alerte > 300:

                message = (
                    f"🚀 <b>ALERTE POMPE DÉTECTÉE !</b>\n\n"
                    f"📌 <b>Crypto :</b> {symbol}\n"
                    f"💰 <b>Prix actuel :</b> ${prix_actuel:.6f}\n"
                    f"📈 <b>Hausse récente :</b> +{hausse_recente:.2f}% en {INTERVALLE_SCAN}s\n"
                    f"📊 <b>Volume :</b> x{ratio_volume:.1f} par rapport à avant\n"
                    f"🕐 <b>Hausse 24h :</b> {hausse_24h:.2f}%\n"
                    f"⏰ <b>Heure :</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
                    f"⚠️ Vérifie avant d'agir !"
                )

                envoyer_alerte(message)
                alertes_envoyees[symbol] = maintenant
                print(f"✅ ALERTE envoyée : {symbol} +{hausse_recente:.2f}%")

    # Sauvegarde les données actuelles
    donnees_precedentes[symbol] = {
        'prix': prix_actuel,
        'volume': volume_actuel
    }
```

def demarrer():
“”“Démarre le scanner”””
print(”=” * 50)
print(“🚀 Scanner Crypto Binance démarré !”)
print(f”📊 Seuil détection : +{SEUIL_HAUSSE_PRIX}% en {INTERVALLE_SCAN}s”)
print(f”📈 Volume minimum : x{SEUIL_HAUSSE_VOLUME}”)
print(”=” * 50)

```
# Envoie un message de démarrage sur Telegram
envoyer_alerte(
    "✅ <b>Scanner Crypto démarré !</b>\n\n"
    f"📊 Détection : +{SEUIL_HAUSSE_PRIX}% en {INTERVALLE_SCAN}s\n"
    f"📈 Volume : x{SEUIL_HAUSSE_VOLUME} minimum\n"
    "🔍 Surveillance de toutes les paires USDT Binance\n\n"
    "Tu recevras une alerte dès qu'une pompe est détectée !"
)

while True:
    print(f"\n🔍 Scan en cours... {datetime.now().strftime('%H:%M:%S')}")
    donnees = recuperer_donnees_binance()
    if donnees:
        analyser_cryptos(donnees)
        print(f"✅ {len(donnees)} cryptos analysées")
    time.sleep(INTERVALLE_SCAN)
```

if **name** == “**main**”:
demarrer()
