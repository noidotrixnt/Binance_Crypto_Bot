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
precio_compra = 104990  # Precio objetivo para comprar
precio_venta = 10500   # Precio objetivo para vender
cantidad = 0.001       # Cantidad de BTC a comprar/vender

# Saldos ficticios para la simulación
saldo_usdt = 0    # Saldo inicial en USDT
saldo_btc = 0.003        # Saldo inicial en BTC

# Configurar logging para registrar simulaciones
logging.basicConfig(
    filename="simulacion_trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Función para obtener el precio actual del par desde Binance
def obtener_precio(par):
    try:
        precio = client.get_symbol_ticker(symbol=par)
        print(f"Precio actual de {par}: {precio['price']}")
        return float(precio['price'])
    except BinanceAPIException as e:
        print(f"Error al obtener el precio: {e}")
        logging.error(f"Error al obtener el precio: {e}")
        return None

# Función para simular una compra
def simular_compra(precio_actual):
    global saldo_usdt, saldo_btc
    costo_total = precio_actual * cantidad
    # Verificar saldo antes de intentar comprar
    if saldo_usdt >= costo_total:
        saldo_usdt -= costo_total
        saldo_btc += cantidad
        print(f"[SIMULACIÓN] Compra: {cantidad} BTC a {precio_actual} USDT")
        print(f"Saldo actual: {saldo_usdt:.2f} USDT, {saldo_btc:.6f} BTC")
        logging.info(f"SIMULACIÓN: Compra: {cantidad} BTC a {precio_actual} USDT. Saldo restante: {saldo_usdt:.2f} USDT, {saldo_btc:.6f} BTC")
    else:
        # No intentar ejecutar la orden, solo mostrar el precio
        print(f"Saldo insuficiente para comprar. Precio actual: {precio_actual:.2f}, Saldo USDT: {saldo_usdt:.2f}")

# Función para simular una venta
def simular_venta(precio_actual):
    global saldo_usdt, saldo_btc
    # Verificar saldo antes de intentar vender
    if saldo_btc >= cantidad:
        saldo_btc -= cantidad
        saldo_usdt += precio_actual * cantidad
        print(f"[SIMULACIÓN] Venta: {cantidad} BTC a {precio_actual} USDT")
        print(f"Saldo actual: {saldo_usdt:.2f} USDT, {saldo_btc:.6f} BTC")
        logging.info(f"SIMULACIÓN: Venta: {cantidad} BTC a {precio_actual} USDT. Saldo restante: {saldo_usdt:.2f} USDT, {saldo_btc:.6f} BTC")
    else:
        # No intentar ejecutar la orden, solo mostrar el precio
        print(f"Saldo insuficiente para vender. Precio actual: {precio_actual:.2f}, Saldo BTC: {saldo_btc:.6f}")

# Estrategia de trading simulada
def estrategia_trading_simulada():
    while True:
        try:
            # Obtener precio real desde Binance
            precio_actual = obtener_precio('BTCUSDT')

            if precio_actual is None:
                time.sleep(10)
                continue

            # Verificar condiciones para comprar o vender
            if precio_actual < precio_compra:
                print("Evaluando posibilidad de compra...")
                simular_compra(precio_actual)
            elif precio_actual > precio_venta:
                print("Evaluando posibilidad de venta...")
                simular_venta(precio_actual)
            else:
                # Si no hay acción, solo muestra el precio
                print(f"El precio actual de BTC es {precio_actual:.2f}, sin cambios en la cuenta.")

            # Pausa entre consultas para evitar límites de la API
            time.sleep(5)

        except Exception as e:
            print(f"Error inesperado: {e}")
            logging.error(f"Error inesperado: {e}")
            time.sleep(10)

# Ejecutar la simulación
estrategia_trading_simulada()