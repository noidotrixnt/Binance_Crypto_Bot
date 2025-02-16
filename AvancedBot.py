''' 
MIT License

Copyright (c) 2025 noidotrixnt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import time
import logging
import pandas as pd
import numpy as np
import config  # Archivo donde guardamos las claves API de Binance

from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.exceptions import BinanceAPIException

# ------------------------------
# Configuración de Logging
# ------------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Handler para archivo
file_handler = logging.FileHandler("trading_bot.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

# Inicializamos el cliente de Binance con nuestras claves API
client = Client(config.API_KEY, config.API_SECRET)

# ------------------------------
# Clase del Bot de Trading
# ------------------------------
class AdvancedTradingBot:
    def __init__(self, client, symbol, interval, short_window, long_window, rsi_period, trailing_stop_percent):
        """
        Inicializa el bot con los parámetros de la estrategia.
        """
        self.client = client
        self.symbol = symbol  # Par de trading, ej. BTCUSDT
        self.interval = interval  # Intervalo de las velas (ej. '1m', '5m')
        self.short_window = short_window  # Ventana corta para la SMA
        self.long_window = long_window  # Ventana larga para la SMA
        self.rsi_period = rsi_period  # Periodo para calcular el RSI
        self.trailing_stop_percent = trailing_stop_percent  # % de trailing stop (ej. 0.02 para 2%)

        # Estado del bot
        self.in_position = False  # Indica si tenemos una posición abierta
        self.buy_price = None  # Precio al que compramos
        self.max_price_since_buy = None  # Precio máximo alcanzado desde la compra

    def get_historical_data(self, lookback="2 hours ago UTC"):
        """
        Obtiene datos históricos (velas) desde Binance y los retorna en un DataFrame.
        """
        try:
            klines = self.client.get_historical_klines(self.symbol, self.interval, lookback)
            if not klines or len(klines) < self.long_window:
                logger.warning("No se obtuvieron suficientes datos históricos.")
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
            logger.error(f"Error al obtener datos históricos: {e}")
            return None

    def compute_indicators(self, df):
        """
        Calcula indicadores técnicos: SMA y RSI.
        """
        if df is None or df.empty:
            return None

        # Cálculo de medias móviles simples (SMA)
        df['SMA_short'] = df['close'].rolling(window=self.short_window, min_periods=1).mean()
        df['SMA_long'] = df['close'].rolling(window=self.long_window, min_periods=1).mean()

        # Cálculo del RSI utilizando el método de medias móviles simples
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        # Cálculo de la media móvil de ganancias y pérdidas
        avg_gain = gain.rolling(window=self.rsi_period, min_periods=1).mean()
        avg_loss = loss.rolling(window=self.rsi_period, min_periods=1).mean().replace(0, 1e-10)
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df

    def generate_signal(self, df):
        """
        Genera señales de compra/venta basado en SMA y RSI.
        """
        last_row = df.iloc[-1]
        sma_short = last_row['SMA_short']
        sma_long = last_row['SMA_long']
        rsi = last_row['RSI']
        current_price = last_row['close']

        signal = 0  # 0: sin acción, 1: señal de compra, -1: señal de venta
        if sma_short > sma_long and rsi < 30:
            signal = 1  # Señal de compra
        elif sma_short < sma_long and rsi > 70:
            signal = -1  # Señal de venta

        return signal, current_price

    def get_balance(self, asset):
        """
        Obtiene el balance disponible del activo.
        """
        try:
            balance_info = self.client.get_asset_balance(asset=asset)
            return float(balance_info['free'])
        except BinanceAPIException as e:
            logger.error(f"Error al obtener balance de {asset}: {e}")
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
            logger.info(f"Orden ejecutada: {order}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Error al colocar orden: {e}")
            return None

    def buy(self, current_price):
        """
        Ejecuta una compra y actualiza el estado del bot.
        """
        usdt_balance = self.get_balance('USDT')
        # Se compra por un valor fijo en USDT, por ejemplo 10 USDT
        quantity = round(10 / current_price, 6)

        if usdt_balance >= (10):  # Verifica que haya al menos 10 USDT disponibles
            logger.info(f"Comprando {quantity} BTC a {current_price} USDT")
            order = self.place_order(SIDE_BUY, quantity)
            if order:
                self.in_position = True
                self.buy_price = current_price
                self.max_price_since_buy = current_price
                logger.info(f"Compra ejecutada a {current_price} USDT")
        else:
            logger.info("Saldo insuficiente para comprar.")

    def sell(self, current_price):
        """
        Ejecuta una venta y resetea el estado del bot.
        """
        btc_balance = self.get_balance('BTC')
        quantity = round(btc_balance, 6)

        if btc_balance > 0:
            logger.info(f"Vendiendo {quantity} BTC a {current_price} USDT")
            order = self.place_order(SIDE_SELL, quantity)
            if order:
                self.in_position = False
                self.buy_price = None
                self.max_price_since_buy = None
                logger.info(f"Venta ejecutada a {current_price} USDT")
        else:
            logger.info("No hay BTC suficiente para vender.")

    def run(self):
        """
        Bucle principal del bot: actualiza indicadores, genera señales y ejecuta órdenes.
        """
        logger.info("Iniciando el bot de trading...")
        try:
            while True:
                df = self.get_historical_data()
                if df is None:
                    time.sleep(60)
                    continue

                df = self.compute_indicators(df)
                if df is None:
                    time.sleep(60)
                    continue

                signal, current_price = self.generate_signal(df)

                if self.in_position:
                    # Actualizar el máximo precio desde la compra
                    self.max_price_since_buy = max(self.max_price_since_buy, current_price)
                    
                    # Verificar si se activa el trailing stop
                    if current_price < self.max_price_since_buy * (1 - self.trailing_stop_percent):
                        logger.info(
                            f"Trailing stop activado: precio actual {current_price} USDT es menor en un {self.trailing_stop_percent*100}% "
                            f"al máximo {self.max_price_since_buy} USDT alcanzado desde la compra."
                        )
                        self.sell(current_price)
                    # También se vende si se genera la señal de venta
                    elif signal == -1:
                        self.sell(current_price)
                else:
                    if signal == 1:
                        self.buy(current_price)

                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Bot detenido por el usuario.")
        except Exception as e:
            logger.error(f"Error en el bucle principal: {e}")

# ------------------------------
# Ejecución del Bot
# ------------------------------
if __name__ == '__main__':
    bot = AdvancedTradingBot(client, 'BTCUSDT', '1m', short_window=7, long_window=21, rsi_period=14, trailing_stop_percent=0.02)
    bot.run()
