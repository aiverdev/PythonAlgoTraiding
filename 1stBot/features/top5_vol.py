from binance.client import Client
import keys as keys
import pandas as pd

client = Client(keys.api_key, keys.api_secret)

def get_top_pairs(base_currency='USDT', top_n=5):
    # Получаем все тикеры
    all_tickers = pd.DataFrame(client.get_ticker())
    
    # Фильтруем пары с базовой валютой base_currency (например, 'USDT')
    base_pairs = all_tickers[all_tickers.symbol.str.contains(base_currency)]
    
    # Сортируем по объему торгов (volume) в убывающем порядке
    top_pairs = base_pairs.sort_values(by='quoteVolume', ascending=False)
    
    # Возвращаем топ N пар
    return top_pairs.head(top_n)

# Получаем топ 5 криптовалют с максимальным объемом торгов с USDT
top_usdt_pairs = get_top_pairs()
print(top_usdt_pairs[['symbol', 'quoteVolume']])
