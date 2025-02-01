import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
import logging

# -----------------------------
# CONFIGURACIÓN DE LA API
# -----------------------------
API_KEY = 'rEpH0ZRmNpD37JnTaqeAXDsvmBDkYFGxGBiycmbT7ftkjmmFvkltsyfoniXLAqe2'
API_SECRET = 'D2SO47457b9RdC0ukgDRNxEygSJhxmIA652U1m3g4cbU1uK3ljEKcouz9WowEaRO'

client = Client(API_KEY, API_SECRET)

# -----------------------------
# CONFIGURACIÓN DE LA ESTRATEGIA
# -----------------------------
# Umbrales para disparar la operación
precio_compra = 104000  # Si el precio actual es menor a este, se ejecuta una compra
precio_venta  = 105000  # Si el precio actual es mayor a este, se ejecuta una venta
cantidad      = 0.0001   # Cantidad de BTC a comprar/vender

# -----------------------------
# CONFIGURACIÓN DE LOGGING
# -----------------------------
logging.basicConfig(
    filename="trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------
def obtener_precio(par: str) -> float:
    """
    Obtiene el precio actual del símbolo especificado.
    """
    try:
        precio_info = client.get_symbol_ticker(symbol=par)
        precio = float(precio_info['price'])
        print(f"Precio actual de {par}: {precio}")
        return precio
    except BinanceAPIException as e:
        print(f"Error al obtener el precio: {e}")
        logging.error(f"Error al obtener el precio: {e}")
        return None

def obtener_balance(asset: str) -> float:
    """
    Consulta el balance disponible para el activo especificado.
    """
    try:
        balance_info = client.get_asset_balance(asset=asset)
        balance = float(balance_info['free'])
        return balance
    except BinanceAPIException as e:
        print(f"Error al obtener balance de {asset}: {e}")
        logging.error(f"Error al obtener balance de {asset}: {e}")
        return 0.0

# -----------------------------
# FUNCIONES PARA OPERAR REALMENTE
# -----------------------------
def realizar_compra(precio_actual: float):
    """
    Ejecuta una orden de compra de mercado para BTC.
    Antes de la compra se consulta el balance USDT.
    """
    usdt_balance = obtener_balance('USDT')
    costo_total = precio_actual * cantidad
    if usdt_balance >= costo_total:
        try:
            order = client.create_order(
                symbol='BTCUSDT',
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=cantidad
            )
            print(f"COMPRA EJECUTADA: {order}")
            logging.info(f"Compra ejecutada: {order}")
        except BinanceAPIException as e:
            print(f"Error al ejecutar la compra: {e}")
            logging.error(f"Error al ejecutar la compra: {e}")
    else:
        mensaje = (f"Saldo insuficiente para comprar. Saldo USDT: {usdt_balance:.2f}, "
                   f"se requiere: {costo_total:.2f}")
        print(mensaje)
        logging.info(mensaje)

def realizar_venta(precio_actual: float):
    """
    Ejecuta una orden de venta de mercado para BTC.
    Antes de la venta se consulta el balance BTC.
    """
    btc_balance = obtener_balance('BTC')
    if btc_balance >= cantidad:
        try:
            order = client.create_order(
                symbol='BTCUSDT',
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=cantidad
            )
            print(f"VENTA EJECUTADA: {order}")
            logging.info(f"Venta ejecutada: {order}")
        except BinanceAPIException as e:
            print(f"Error al ejecutar la venta: {e}")
            logging.error(f"Error al ejecutar la venta: {e}")
    else:
        mensaje = (f"Saldo insuficiente para vender. Saldo BTC: {btc_balance:.6f}, "
                   f"se requiere: {cantidad:.6f}")
        print(mensaje)
        logging.info(mensaje)

# -----------------------------
# ESTRATEGIA DE TRADING REAL
# -----------------------------
def estrategia_trading_real():
    """
    Función principal que consulta el precio de BTCUSDT cada 5 segundos y
    ejecuta una orden de compra si el precio es menor a 'precio_compra'
    o una orden de venta si el precio es mayor a 'precio_venta'.
    """
    while True:
        try:
            precio_actual = obtener_precio('BTCUSDT')
            if precio_actual is None:
                time.sleep(10)
                continue

            if precio_actual < precio_compra:
                print("Condición de compra cumplida. Ejecutando compra...")
                realizar_compra(precio_actual)
            elif precio_actual > precio_venta:
                print("Condición de venta cumplida. Ejecutando venta...")
                realizar_venta(precio_actual)
            else:
                print(f"El precio actual de BTC es {precio_actual:.2f}, sin condiciones para operar.")

            # Pausa para no exceder límites de la API
            time.sleep(5)

        except Exception as e:
            print(f"Error inesperado: {e}")
            logging.error(f"Error inesperado: {e}")
            time.sleep(10)

# -----------------------------
# EJECUCIÓN DEL BOT
# -----------------------------
if __name__ == "__main__":
    estrategia_trading_real()
