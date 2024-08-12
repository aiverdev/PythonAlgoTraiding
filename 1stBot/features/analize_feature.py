from binance.client import Client
from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt
import keys as keys

client = Client(keys.api_key, keys.api_secret)


def get_historical_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + 'min ago UTC'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

def prophet_forecast(df):
    df_prophet = df[['Close']].reset_index().rename(columns={'Time': 'ds', 'Close': 'y'})
    model = Prophet()
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=5, freq='H')
    forecast = model.predict(future)
    
    # Визуализируем результаты
    fig = model.plot(forecast)
    plt.title(f'Forecast for {symbol}')
    plt.show()
    
    return forecast

# Использование функции
symbol = 'BTCUSDT'  # Пример пары
df = get_historical_data(symbol, '1h', '720')
forecast = prophet_forecast(df)

# Выводим последние прогнозы
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(10))
