from binance.client import Client
import time

API_KEY = 'rEpH0ZRmNpD37JnTaqeAXDsvmBDkYFGxGBiycmbT7ftkjmmFvkltsyfoniXLAqe2'
API_SECRET = 'D2SO47457b9RdC0ukgDRNxEygSJhxmIA652U1m3g4cbU1uK3ljEKcouz9WowEaRO'

client = Client(API_KEY, API_SECRET)

def obtener_precio(par):
    precio = client.get_symbol_ticker(symbol=par)
    print(f"El precio actual de {par} es: {precio['price']}")
    return float(precio['price'])

obtener_precio('BTCUSDT')
obtener_precio('ETHUSDT')
obtener_precio('SOLUSDT')

precio_compra = 96000
precio_venta = 96650 
cantidad = 0.00001 

def estrategia_trading():
    while True:
        precio_actual = obtener_precio('BTCUSDT')

        if precio_actual < precio_compra:
            print("Ejecutando orden de compra...")
            client.order_market_buy(
                symbol='BTCUSDT',
                quantity=cantidad
            )
            print(f"Comprado {cantidad} BTC a {precio_actual}")

        elif precio_actual > precio_venta:
            print("Ejecutando orden de venta...")
            client.order_market_sell(
                symbol='BTCUSDT',
                quantity=cantidad
            )
            print(f"Vendido {cantidad} BTC a {precio_actual}")

        time.sleep(2)


estrategia_trading()

