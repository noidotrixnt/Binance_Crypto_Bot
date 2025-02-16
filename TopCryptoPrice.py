from binance.client import Client
import time
import config


client = Client(config.API_KEY, config.API_SECRET)

def obtener_precio(par):
    
    precio = client.get_symbol_ticker(symbol=par)
    print(f"El precio actual de {par} es: {precio['price']}")
    return float(precio['price'])
while True:
    # obtener_precio('BTCUSDT')
    obtener_precio('ETHUSDT')
    # obtener_precio('SOLUSDT')
    # obtener_precio('BNBUSDT')
    # obtener_precio('DOGEUSDT')
    # obtener_precio('PEPEUSDT')
    time.sleep(5)