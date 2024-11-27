from binance.client import Client
import time

API_KEY = 'rEpH0ZRmNpD37JnTaqeAXDsvmBDkYFGxGBiycmbT7ftkjmmFvkltsyfoniXLAqe2'
API_SECRET = 'D2SO47457b9RdC0ukgDRNxEygSJhxmIA652U1m3g4cbU1uK3ljEKcouz9WowEaRO'

client = Client(API_KEY, API_SECRET)

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