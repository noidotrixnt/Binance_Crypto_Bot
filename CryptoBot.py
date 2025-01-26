import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
import logging

# Configuración de claves API
API_KEY = 'rEpH0ZRmNpD37JnTaqeAXDsvmBDkYFGxGBiycmbT7ftkjmmFvkltsyfoniXLAqe2'
API_SECRET = 'D2SO47457b9RdC0ukgDRNxEygSJhxmIA652U1m3g4cbU1uK3ljEKcouz9WowEaRO'

# Inicializar cliente de Binance
client = Client(API_KEY, API_SECRET)

# Configuración de la estrategia
precio_compra = 96100  # Precio objetivo para comprar
precio_venta = 96150   # Precio objetivo para vender
cantidad = 0.001       # Cantidad de BTC a comprar/vender

# Configurar logging para registrar errores y operaciones
logging.basicConfig(
    filename="trading_bot_real.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Función para obtener el precio actual del par
def obtener_precio(par):
    try:
        precio = client.get_symbol_ticker(symbol=par)
        print(f"El precio actual de {par} es: {precio['price']}")
        return float(precio['price'])
    except BinanceAPIException as e:
        print(f"Error al obtener el precio: {e}")
        logging.error(f"Error al obtener el precio: {e}")
        return None

# Función para verificar el saldo disponible
def verificar_saldo(symbol, cantidad):
    try:
        balances = client.get_account()
        for balance in balances['balances']:
            if balance['asset'] == symbol:
                disponible = float(balance['free'])
                print(f"Saldo disponible de {symbol}: {disponible}")
                return disponible >= cantidad
        return False
    except BinanceAPIException as e:
        print(f"Error al verificar el saldo: {e}")
        logging.error(f"Error al verificar el saldo: {e}")
        return False

# Función para realizar una compra real
def ejecutar_compra(symbol, cantidad):
    try:
        orden = client.order_market_buy(
            symbol=symbol,
            quantity=cantidad
        )
        print(f"Compra ejecutada: {orden}")
        logging.info(f"Compra ejecutada: {orden}")
    except BinanceAPIException as e:
        if "insufficient balance" in str(e):
            print("Error: No tienes suficiente saldo para realizar la compra.")
            logging.error("Error: Saldo insuficiente para la compra.")
        else:
            print(f"Error al realizar la compra: {e}")
            logging.error(f"Error al realizar la compra: {e}")

# Función para realizar una venta real
def ejecutar_venta(symbol, cantidad):
    try:
        orden = client.order_market_sell(
            symbol=symbol,
            quantity=cantidad
        )
        print(f"Venta ejecutada: {orden}")
        logging.info(f"Venta ejecutada: {orden}")
    except BinanceAPIException as e:
        if "insufficient balance" in str(e):
            print("Error: No tienes suficiente saldo para realizar la venta.")
            logging.error("Error: Saldo insuficiente para la venta.")
        else:
            print(f"Error al realizar la venta: {e}")
            logging.error(f"Error al realizar la venta: {e}")

# Estrategia de trading
def estrategia_trading():
    while True:
        try:
            # Obtener precio actual
            precio_actual = obtener_precio('BTCUSDT')

            if precio_actual is None:
                time.sleep(10)
                continue

            # Verificar y ejecutar compra
            if precio_actual < precio_compra:
                print("Verificando saldo para comprar...")
                if verificar_saldo('USDT', cantidad * precio_actual):
                    print("Ejecutando orden de compra...")
                    ejecutar_compra('BTCUSDT', cantidad)
                else:
                    print("Saldo insuficiente para la compra.")

            # Verificar y ejecutar venta
            elif precio_actual > precio_venta:
                print("Verificando saldo para vender...")
                if verificar_saldo('BTC', cantidad):
                    print("Ejecutando orden de venta...")
                    ejecutar_venta('BTCUSDT', cantidad)
                else:
                    print("Saldo insuficiente para la venta.")

            # Pausa entre consultas para evitar límites de la API
            time.sleep(5)

        except Exception as e:
            print(f"Error inesperado: {e}")
            logging.error(f"Error inesperado: {e}")
            time.sleep(10)

# Ejecutar el bot
estrategia_trading()
