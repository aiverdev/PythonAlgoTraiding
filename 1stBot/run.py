from binance.client import Client
import keys as keys
import pandas as pd
import time


client = Client(keys.api_key, keys.api_secret)

print('ВАЖНО! Необходимо учитывать: ')
print('* Коммиссия за каждую операцию (покупка/продажа) составляет - 0.1%')
print('* Для некоторых монет минимальный объем (minQTY): 5 коинов')
print('* При вводе суммы помните про STOP-LOSS и КОММИССИЮ х2 (0.2%)')
print('* МИНИМАЛЬНАЯ РЕКОМЕНДУЕМАЯ СУММА: 10 коинов')
buy_amt = float(input("ВВЕДИТЕ СУММУ ПЛАНИРУЕМОЙ СДЕЛКИ: ")) # ВВОД СУММЫ (USDT)



# ======================== ПОИСК АКТИВНОЙ МОНЕТЫ ========================
def top_coin():

    all_tickers = pd.DataFrame(client.get_ticker())
    coin = all_tickers[all_tickers.symbol.str.contains('USDT')]
    work = coin[~((coin.symbol.str.contains('UP')) | (coin.symbol.str.contains('DOWN'))) ]
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]
    return top_coin

print(top_coin()) # распечатываем выбранную ботом монету



# ======================== ИСТОРИЧЕСКИЕ ДАННЫЕ ========================
def last_data(symbol, interval, lookback):

    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + 'min ago UTC'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame



# ======================== ТОРГОВАЯ СТРАТЕГИЯ ========================
def strategy(buy_amt, SL=0.985, Target=1.02, open_position=False):
    try:
        asset = top_coin()
        df = last_data(asset, '1m', '120')
    except:
        time.sleep(61)
        asset = top_coin()
        df = last_data(asset, '1m', '120')

    # ======================== ОБЪЕМ  ========================
    qty = round(buy_amt/df.Close.iloc[-1] ,1) # закупаемый объем монет
    qty_o = round(qty + (qty * 0.2 / 100)) # закупаемый объем + 0.2% коммиссионные
    qty_c = round(qty - (qty * 0.2 / 100)) # закупаемый объем + 0.2% коммиссионные

    # ================== ДАННЫЕ О МОНЕТЕ ==================
    info = client.get_symbol_info(asset)
    print(f' ================== ДАННЫЕ О МОНЕТЕ ================== ')
    print(info) # Выводим данные о монете
    # Узнаем минимальный объем (USDT) для открытия ордера = minQty (LOT_SIZE)
    minQty = info['filters'][1]['minQty']
    # Узнаем минимальный объем (USDT) для закрытия ордера = minNotional (NOTIONAL)
    # minNotional определяет минимальную условную стоимость, необходимую для каждого заказа
    minNotional = info['filters'][6]['minNotional']
    print(f' ====================================================== ')

    print(f' ')
    print(f'ПАРА: ' + str(asset))
    print(f'ПОСЛЕДНЯЯ ЦЕНА: ' + str(df.Close.iloc[-1]))
    print(f'БЮДЖЕТ НА СДЕЛКУ: ' + str(buy_amt))
    print(f'ЗАКУПАЕМЫЙ ОБЪЕМ МОНЕТ: ' + str(qty))
    print(f'МИНИМАЛЬНЫЙ ОБЪЕМ (USDT) НА ЗАКУП: ' + str(minQty))
    print(f'МИНИМАЛЬНЫЙ ОБЪЕМ (USDT) ДЛЯ ЗАКРЫТИЯ СДЕЛКИ: ' + str(minNotional))
    print(f'ОЖИДАЕМЫЙ БАЛАНС МОНЕТ после вычета КОММИССИИ: ' + str(qty - (qty * 0.1 / 100)))
    print(f' ')

    # ======================== ОТКРЫТИЕ ОРДЕРА ========================
    if ((df.Close.pct_change() + 1).cumprod()).iloc[-1] > 1:
        print(f'КОИН: ' + str(asset))
        print(f'ЦЕНА ПОКУПКИ: ' + str(df.Close.iloc[-1]))
        print(f'ЗАКУПЛЕННЫЙ ОБЪЕМ: ' + str(qty_o))
        order = client.create_order(symbol=asset, side='BUY', type='MARKET', quantity = qty_o)
        print(order)
        buyprice = float(order['fills'][0]['price'])

        trade_qty = float(order['fills'][0]['qty'])
        commission = float(order['fills'][0]['commission'])
        balance = trade_qty - commission
        usdt_in_c = balance * df.Close.iloc[-1]
        print(f' ----------------------- ')
        print(f'ORDER-info: ')
        print(f'ЦЕНА ПОКУПКИ: ' + str(buyprice))
        print(f'ЦЕЛЬ: ' + str(buyprice * Target))
        print(f'СТОП: ' + str(buyprice * SL))
        print(f'БАЛАНС МОНЕТ: ' + str(balance))
        print(f'ОБЪЕМ МОНЕТ: ' + str(trade_qty))
        print(f'ОБЪЕМ МОНЕТ в USDT: ' + str(usdt_in_c))
        print(f'КОММИССИЯ: ' + str(commission))
        print(f' ----------------------- ')
        open_position = True
        # ======================== ЗАКРЫТИЕ ОРДЕРА ========================
        while open_position:
            try:
                df = last_data(asset, '1m', '2')
            except:
                print('ПЕРЕРЫВ на МИНУТОЧКУ!')
                time.sleep(61)
                df = last_data(asset, '1m', '2')
            
            print(f' ')
            print(f'Монета (asset): ' + str(asset))
            print(f'Баланс (trade_qty): ' + str(trade_qty))
            print(f'Баланс в USDT (usdt_in_c): ' + str(usdt_in_c))
            print(f'Цена сейчас: ' + str(df.Close.iloc[-1]))
            print(f'Target ' + str(buyprice * Target))
            print(f'Stop ' + str(buyprice * SL))
            if df.Close[-1] <= buyprice * SL or df.Close[-1] >= buyprice * Target:
                order = client.create_order(symbol=asset, side='SELL', type='MARKET', quantity = qty_c)
                print(order)
                break
    else:
        print('ПОДХОДЯЩЕЙ ПАРЫ НЕ НАЙДЕНО!')
        time.sleep(20)
# ЗАПУСК СТРАТЕГИИ
while True:
    strategy(buy_amt)