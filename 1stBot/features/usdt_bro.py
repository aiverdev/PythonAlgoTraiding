from binance.client import Client
import keys as keys
import pandas as pd

client = Client(keys.api_key, keys.api_secret)

def get_near_one_ratio_pairs(base_currency='USDT', tolerance=0.01):
    # Получаем все тикеры
    all_tickers = pd.DataFrame(client.get_ticker())
    
    # Фильтруем пары с базовой валютой base_currency (например, 'USDT')
    base_pairs = all_tickers[all_tickers.symbol.str.contains(base_currency)]
    
    # Преобразуем цену в float
    base_pairs['lastPrice'] = base_pairs['lastPrice'].astype(float)
    
    # Вычисляем разницу от 1 USDT
    base_pairs['difference_from_one'] = abs(base_pairs['lastPrice'] - 1)
    
    # Фильтруем пары, где разница меньше заданной допустимой величины
    near_one_pairs = base_pairs[base_pairs['difference_from_one'] <= tolerance]
    
    # Сортируем по разнице от 1 USDT
    near_one_pairs = near_one_pairs.sort_values(by='difference_from_one')
    
    return near_one_pairs[['symbol', 'lastPrice', 'difference_from_one']]

# Получаем пары, которые близки к соотношению 1:1
near_one_pairs = get_near_one_ratio_pairs()
print(near_one_pairs)
