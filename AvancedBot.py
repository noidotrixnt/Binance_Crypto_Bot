import os
import time
import logging
import pandas as pd
import numpy as np
from dotenv import load_dotenv  # Importa la librería para cargar variables de entorno
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.exceptions import BinanceAPIException

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las API keys desde las variables de entorno
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("Faltan las API keys. Verifica que BINANCE_API_KEY y BINANCE_API_SECRET estén definidas en el archivo .env.")

client = Client(API_KEY, API_SECRET)

# ------------------------------
# Configuración de Logging
# ------------------------------
logging.basicConfig(
    filename="advanced_trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------------------
# Clase del Bot Avanzado de Trading
# ------------------------------
class AdvancedTradingBot:
    def __init__(self, client, symbol, interval, short_window, long_window, rsi_period, trailing_stop_percent):
        self.client = client
        self.symbol = symbol
        self.interval = interval
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_period = rsi_period
        self.trailing_stop_percent = trailing_stop_percent

        # Variables para gestionar la posición
        self.in_position = False
        self.buy_price = None
        self.max_price_since_buy = None

    def get_historical_data(self, lookback="2 hours ago UTC"):
        """
        Obtiene datos históricos (klines) y retorna un DataFrame.
        """
        try:
            klines = self.client.get_historical_klines(self.symbol, self.interval, lookback)
            if not klines:
                logging.warning("No se obtuvieron datos históricos.")
                return None
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['close'] = df['close'].astype(float)
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            return df
        except BinanceAPIException as e:
            logging.error(f"Error al obtener datos históricos: {e}")
            return None

    def compute_indicators(self, df):
        """
        Calcula dos medias móviles (SMA) y el RSI sobre el precio de cierre.
        """
        # Medias Móviles
        df['SMA_short'] = df['close'].rolling(window=self.short_window).mean()
        df['SMA_long'] = df['close'].rolling(window=self.long_window).mean()
        
        # Cálculo del RSI
        delta = df['close'].diff()
        gain = delta.copy()
        loss = delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.abs().rolling(window=self.rsi_period).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df

    def generate_signal(self, df):
        """
        Genera una señal basada en el cruce de SMA y en el RSI:
          - Señal de COMPRA (1): SMA de corto plazo > SMA de largo plazo y RSI < 30.
          - Señal de VENTA (-1): SMA de corto plazo < SMA de largo plazo y RSI > 70.
          - Caso contrario, 0 (sin acción).
        """
        last_row = df.iloc[-1]
        sma_short = last_row['SMA_short']
        sma_long = last_row['SMA_long']
        rsi = last_row['RSI']
        current_price = last_row['close']

        signal = 0
        if sma_short > sma_long and rsi < 30:
            signal = 1  # Condición de compra
        elif sma_short < sma_long and rsi > 70:
            signal = -1  # Condición de venta

        return signal, current_price

    def get_balance(self, asset):
        """
        Retorna el balance libre para el activo especificado.
        """
        try:
            balance_info = self.client.get_asset_balance(asset=asset)
            return float(balance_info['free'])
        except BinanceAPIException as e:
            logging.error(f"Error al obtener balance de {asset}: {e}")
            return 0.0

    def place_order(self, side, quantity):
        """
        Ejecuta una orden de mercado.
        """
        try:
            order = self.client.create_order(
                symbol=self.symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            logging.info(f"Orden ejecutada: {order}")
            print(f"Orden ejecutada: {order}")
            return order
        except BinanceAPIException as e:
            logging.error(f"Error al colocar orden: {e}")
            print(f"Error al colocar orden: {e}")
            return None

    def buy(self, current_price):
        """
        Ejecuta una orden de compra y actualiza el estado de la posición.
        """
        usdt_balance = self.get_balance('USDT')
        quantity = 0.001  # Puedes ajustar la cantidad o calcularla dinámicamente
        cost = current_price * quantity
        if usdt_balance >= cost:
            order = self.place_order(SIDE_BUY, quantity)
            if order:
                self.in_position = True
                self.buy_price = current_price
                self.max_price_since_buy = current_price
                logging.info(f"Compra ejecutada a {current_price} USDT")
        else:
            logging.info(f"Saldo insuficiente para comprar. Balance USDT: {usdt_balance:.2f}, se requiere: {cost:.2f}")

    def sell(self, current_price):
        """
        Ejecuta una orden de venta y resetea el estado de la posición.
        """
        btc_balance = self.get_balance('BTC')
        quantity = 0.001  # Debe coincidir con la cantidad utilizada en la compra
        if btc_balance >= quantity:
            order = self.place_order(SIDE_SELL, quantity)
            if order:
                self.in_position = False
                self.buy_price = None
                self.max_price_since_buy = None
                logging.info(f"Venta ejecutada a {current_price} USDT")
        else:
            logging.info(f"Saldo insuficiente para vender. Balance BTC: {btc_balance:.6f}, se requiere: {quantity:.6f}")

    def run(self):
        """
        Bucle principal del bot: cada minuto se actualizan los indicadores, se verifica la señal y se
        ejecutan las operaciones correspondientes.
        """
        while True:
            df = self.get_historical_data()
            if df is None or df.empty:
                logging.warning("No se pudieron obtener datos; reintentando en 60 segundos.")
                time.sleep(60)
                continue

            df = self.compute_indicators(df)
            signal, current_price = self.generate_signal(df)
            print(f"Señal: {signal}, Precio actual: {current_price}")

            # Si ya tenemos posición abierta, actualizar el precio máximo alcanzado
            if self.in_position:
                if current_price > self.max_price_since_buy:
                    self.max_price_since_buy = current_price
                    logging.info(f"Actualizado max_price_since_buy: {self.max_price_since_buy}")

                # Verificar si se activa el trailing stop
                if current_price < self.max_price_since_buy * (1 - self.trailing_stop_percent):
                    print("Trailing stop activado. Ejecutando venta.")
                    logging.info("Trailing stop activado. Ejecutando venta.")
                    self.sell(current_price)
                    # Tras la venta, continuar sin evaluar otras señales en este ciclo
                    time.sleep(60)
                    continue

            # Ejecutar órdenes según la señal generada y el estado de la posición
            if not self.in_position and signal == 1:
                print("Señal de COMPRA detectada. Ejecutando compra.")
                logging.info("Señal de COMPRA detectada. Ejecutando compra.")
                self.buy(current_price)
            elif self.in_position and signal == -1:
                print("Señal de VENTA detectada. Ejecutando venta.")
                logging.info("Señal de VENTA detectada. Ejecutando venta.")
                self.sell(current_price)
            
            # Esperar 60 segundos para que se cierre la vela y se actualicen los indicadores
            time.sleep(60)

# ------------------------------
# Ejecución del Bot
# ------------------------------
if __name__ == '__main__':
    # Parámetros de la estrategia
    symbol = 'BTCUSDT'
    interval = '1m'          # Intervalo de las velas (1 minuto)
    short_window = 7         # Ventana corta para la SMA
    long_window = 21         # Ventana larga para la SMA
    rsi_period = 14          # Periodo para el RSI
    trailing_stop_percent = 0.02  # Trailing stop del 2%

    bot = AdvancedTradingBot(client, symbol, interval, short_window, long_window, rsi_period, trailing_stop_percent)
    bot.run()
