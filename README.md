⚠️ **DISCLAIMER:** 
This trading bot uses Binance's API but is not affiliated with, endorsed, or certified by Binance.  
Use this software at your own risk. The developers are not responsible for financial losses, bot malfunctions, or changes in Binance’s API.

# Work in progress!!

# 🚀 Advanced Binance Trading Bot

A fully automated **crypto trading bot** that uses **Simple Moving Averages (SMA)** and **Relative Strength Index (RSI)** to execute buy and sell orders on Binance. It also features **Trailing Stop Loss** to maximize profits and minimize losses.

## 📌 Features
✅ Uses **SMA (7, 21)** and **RSI (14)** for trade signals.  
✅ Implements a **Trailing Stop Loss** mechanism.  
✅ Automates buying and selling in the Binance **Spot Market**.  
✅ Logs all trades and errors to a file (`trading_bot.log`).  
✅ Includes **exception handling** for better stability.  

---

## 🛠 Installation & Dependencies

### 1️⃣ **Clone the repository**
```bash
git clone https://github.com/noidotrixnt/binance-trading-bot.git
cd binance-trading-bot
```

### 2️⃣ **Create a virtual environment (optional, but recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

### 📌 **Required Dependencies**
| Package      | Description |
|-------------|------------|
| `python-binance` | Official Binance API wrapper for Python |
| `pandas` | Data analysis and handling of historical price data |
| `numpy` | For calculations like RSI and moving averages |
| `logging` | Logs bot activity to a file |

**Make sure you have Python 3.8+ installed.**  

---

## ⚙️ Configuration

### 1️⃣ **Set up your Binance API Keys**
Create a `config.py` file inside the project directory and add your API keys:
```python
API_KEY = "your_binance_api_key"
API_SECRET = "your_binance_secret_key"
```
❌ **DO NOT** commit your `config.py` file to GitHub!  
✅ Use a `.gitignore` file to exclude it.

### 2️⃣ **Modify trading parameters (Optional)**
Inside `bot.py`, adjust the following:
```python
symbol = "BTCUSDT"   # Change to any trading pair (e.g., ETHUSDT)
interval = "1m"      # Change candle interval ('5m', '15m', etc.)
short_window = 7     # Short-term SMA
long_window = 21     # Long-term SMA
rsi_period = 14      # RSI period
trailing_stop = 0.02 # 2% Trailing Stop Loss
```

---

## 🚀 Running the Bot

Once configured, start the bot with:
```bash
python bot.py
```
The bot will:
- Fetch **historical price data** from Binance.
- Calculate **SMA (7, 21)** and **RSI (14)**.
- Generate **buy and sell signals** based on indicators.
- **Automatically place market orders** on Binance.
- Monitor **price fluctuations** and **apply trailing stop-loss**.

📌 **Logs are saved in** `trading_bot.log`.

---

## ⚠️ Disclaimer  

**This trading bot is provided as-is, without warranty of any kind.**  
You are solely responsible for any financial risks involved.  
This bot uses **Binance's API** but is **not affiliated with, endorsed, or certified by Binance**.

**By using this bot, you agree that the developers are not responsible for any losses or malfunctions.**  

🚀 **Happy Trading!**