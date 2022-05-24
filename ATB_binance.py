import time
import ccxt 
import pandas as pd 
import numpy as np
from datetime import datetime
import datetime

while True: 
  import datetime
  now = datetime.datetime.now()
  #값 불러와서 데이터 정리
  #print("#####################################################",now ,"#########################################################")

  what_do_you_want = "MANA/USDT"
  what_to_buy = "MANAUSDT"
  what_time = '1m'
  binance = ccxt.binance()
  btc_ohlcv = binance.fetch_ohlcv(what_do_you_want, what_time)

  df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
  df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
  df.set_index('datetime', inplace=True)

  # 인덱스 리셋
  df = df.reset_index()





  #rsi 지수 구하기 n =14
  RSI_n=14
  df["등락"]=[df.loc[i,'close']-df.loc[i-1,'close'] if i>0 else 0 for i in range(len(df))] 
  df["RSI_U"]=df["등락"].apply(lambda x: x if x>0 else 0)
  df["RSI_D"]=df["등락"].apply(lambda x: x * (-1) if x<0 else 0)
  df["RSI_AU"]=df["RSI_U"].rolling(RSI_n).mean()
  df["RSI_AD"]=df["RSI_D"].rolling(RSI_n).mean()
  df["RSI"] = df.apply(lambda x:x["RSI_AU"]/(x["RSI_AU"]+ x["RSI_AD"]) * 100,1)

  # 일반 rsi -> 거래소 rsi
  for ten in range(15,500) :
    df.loc[ten,'RSI'] = (1-1/14)*df.loc[ten-1,'RSI']+(1/14*df.loc[ten,'RSI'])



  # close 피크, high, low RSI peak 설정
  df['high RSI peak?'] = np.where(df['RSI']>=0, 'N', 1)
  df['low RSI peak?'] = np.where(df['RSI']>=0, 'N', 1)
  for a in range(1,499):
    past = df.loc[a-1,'RSI']
    now = df.loc[a,'RSI']
    future = df.loc[a+1,'RSI']
    if past <= now and future <= now:
      df.loc[a,'high RSI peak?'] = 'Y'
      if df.loc[a, 'RSI'] < 50:
        df.loc[a,'high RSI peak?'] = 'N'
      
    if past >= now and future >= now:
      df.loc[a,'low RSI peak?'] = 'Y'
      if df.loc[a, 'RSI'] > 50:
        df.loc[a,'high RSI peak?'] = 'N'


  #다이버전스 탐색
  df['하락 다이버전스?'] = np.where(df['close']>0, 'N', 1)
  df['상승 다이버전스?'] = np.where(df['close']>0, 'N', 1)

  for b in range(30,500):
    if df.loc[b,'high RSI peak?'] == 'Y':
      past_RSI_high = df.loc[b,'RSI']
      for c in range(5,30):
        if b+c >= 500 or df.loc[b+c-1,'하락 다이버전스?']=='Y':
          break
        if df.loc[b+c,'high RSI peak?'] == 'Y':
          future_RSI_high = df.loc[b+c,'RSI']
          past_high = df.loc[b,'high']
          future_high = df.loc[b+c, 'high']
          if past_high <= future_high and past_RSI_high >= future_RSI_high:
            df.loc[b+c,'하락 다이버전스?'] = 'Y' 
            for diver_check in range(b,b+c+1) :
              if past_RSI_high < df.loc[diver_check,'RSI']:
                df.loc[b+c,'하락 다이버전스?'] = 'N'

            break

  for b in range(0,500):
    if df.loc[b,'low RSI peak?'] == 'Y':
      past_RSI_low = df.loc[b,'RSI']
      for c in range(5,30):
        if b+c >= 500 or df.loc[b+c-1,'상승 다이버전스?']=='Y':
          break
        if df.loc[b+c,'low RSI peak?'] == 'Y':
          future_RSI_low = df.loc[b+c,'RSI']
          past_low = df.loc[b,'low']
          future_low = df.loc[b+c, 'low']
          if past_low > future_low and past_RSI_low < future_RSI_low:
            df.loc[b+c,'상승 다이버전스?'] = 'Y' 
            for diver_check in range(b,b+c+1) :
              if past_RSI_low > df.loc[diver_check,'RSI']:
                df.loc[b+c,'상승 다이버전스?'] = 'N'
            break

  for divergence_editor in range(15,500):
    if df.loc[divergence_editor,'하락 다이버전스?'] == 'Y' and df.loc[divergence_editor-1,'RSI'] < 50 :
      df.loc[divergence_editor,'하락 다이버전스?'] = 'N'
    if df.loc[divergence_editor,'상승 다이버전스?'] == 'Y' and df.loc[divergence_editor-1,'RSI'] > 50 :
      df.loc[divergence_editor,'상승 다이버전스?'] = 'N'
  









  # 하락 다이버전스 내에서 최저값 찾기
  df['하다 회수구간'] = np.where(df['close']>0, 'N', 1)
  real_sum = 0
  real_sum1 = 0


  for g in range(499,0,-1):
    predictable_profit = 0
    predictable_loss = 0
    if df.loc[g,'하락 다이버전스?'] == 'Y':
      now_divergence = g
      for h in range(1,25):
        if g-h <= 0 or g-h>=500 :
          break
        if df.loc[g-h,'high RSI peak?'] == 'Y':
          divergence_len = h
          break
      i=[]
      for j in range(g-h, g+1):
       i.append(j)
      most_low_RSI = min(df.loc[i,'RSI'])
      most_low_price = min(df.loc[i,'low'])
      now_divergence_close = df.loc[now_divergence,'close']
      for q in range(20):
        if now_divergence + q > 499 :
          break
        if df.loc[now_divergence + q,'RSI'] < most_low_RSI or df.loc[now_divergence +q, 'low'] < most_low_price :
          predictable_profit = ((now_divergence_close - df.loc[now_divergence + q , 'close'])/now_divergence_close)*100
          print("$$이득입니다! 예상되는 이득은", predictable_profit, "% 입니다.$$ 현재 다이버전스는 ", now_divergence,"에 위치하고 있습니다.", q,  "번째 다음 이득이 나타납니다." )
          df.loc[now_divergence + q,'하다 회수구간'] = 'Y'
          break
        if df.loc[now_divergence-1,'high']*1.02 < df.loc [now_divergence+q,'close'] or q == 19:
          predictable_loss = ((now_divergence_close - df.loc[499,'close'])/now_divergence_close)*100
          print("손해입니다. 손해금액은",predictable_loss,"입니다.", "위치는", now_divergence + q ,"이며," ,q, "번째 다음 손해가 나타납니다.")
          df.loc[now_divergence + q,'하다 회수구간'] = 'Y'
          break
    real_sum += predictable_loss + predictable_profit
  print("하락다이버 후 이득   ", real_sum)      






  # 상승 다이버전스 내에서 최저값 찾기
  df['상다 회수구간'] = np.where(df['close']>0, 'N', 1)
  for g1 in range(499,0,-1):
    predictable_profit1 = 0
    predictable_loss1 = 0
    if df.loc[g1,'상승 다이버전스?'] == 'Y':
      now_divergence1 = g1
      for h2 in range(1,25):
        if g1-h2 <0 or g1-h2>=500 :
          break
        if df.loc[g1-h2,'low RSI peak?'] == 'Y':
          divergence_len1 = h2
          break
      i=[]
      for j1 in range(now_divergence1 - h2, now_divergence1+1):
       i.append(j1)
      most_high_RSI = max(df.loc[i,'RSI'])
      most_high_price = max(df.loc[i,'high'])
      now_divergence_low_close = df.loc[now_divergence1,'close']
      for q1 in range(20):
        if now_divergence1 + q1 > 499 :
          break
        if df.loc[now_divergence1 + q1,'RSI'] > most_high_RSI or df.loc[now_divergence1 +q1, 'high'] > most_high_price :
          predictable_profit1 = ((df.loc[now_divergence1 + q1,'close'] - now_divergence_low_close)/now_divergence_low_close)*100
          print("$$이득입니다! 예상되는 이득은", predictable_profit1, "% 입니다.$$ 현재 다이버전스는 ", now_divergence1,"에 위치하고 있습니다.", q1,  "번째 다음 이득이 나타납니다." )
          df.loc[now_divergence1 + q1,'상다 회수구간'] = 'Y'
          break
        if df.loc[now_divergence1-1,'low']*0.98 > df.loc [now_divergence1+q1,'close'] or q1 == 19:
          predictable_loss1 = ((now_divergence_low_close - df.loc[499,'close'])/now_divergence_low_close)*100
          print("손해입니다. 손해금액은",predictable_loss1,"입니다.", "위치는", now_divergence1 ,"이며," ,q1, "번째 다음 손해가 나타납니다.")
          df.loc[now_divergence1 + q1,'상다 회수구간'] = 'Y'
          break
    real_sum1 += predictable_loss1 + predictable_profit1
  print("상승다이버 후 이득   ", real_sum1)      









  ############################################################ 구매 함수 ######################################################################


  ############################################ 구매함수 시작 ######################################################
  import datetime
  now = datetime.datetime.now()
  api_key = "api 입력"
  secret  = "api 입력"

  binance = ccxt.binance(config={
      'apiKey': api_key, 
      'secret': secret,
      'enableRateLimit': True,
      'options': {
          'defaultType': 'future'
      }
  })

  balance = binance.fetch_balance(params={"type": "future"})

  # 최대 구매값 구하기
  import pandas as pd
  from datetime import datetime

  api_key = "api 입력"
  secret  = "api 입력"

  binance = ccxt.binance(config={
      'apiKey': api_key, 
      'secret': secret,
      'enableRateLimit': True,
      'options': {
          'defaultType': 'future'
      }
  })
  now_balance = balance['USDT']['total']
  now_close_price= df.loc[499,'close']
  maximum_amount = now_balance//now_close_price



  if balance['USDT']['used'] > 0 : 
      if df.loc[499,'하다 회수구간'] == 'Y' or df.loc[498,'하다 회수구간'] == 'Y' :
        #포지션 수량 찾기
        positions = balance['info']['positions']
        for position in positions:
          if position["symbol"] == what_to_buy:
            now_amount = position['positionAmt']
            now_amount = int(now_amount)


        if now_amount < 0:
          order = binance.create_market_buy_order(
          symbol= what_do_you_want,
          amount= -(now_amount)
          )
          print(what_do_you_want,"를", now_amount,"만큼 숏포지션을 정리하였습니다! 현재시간은", now ,"입니다.")

      
        

  if balance['USDT']['used'] == 0 : 
    #print("하락다이버전스--------------------------------")
    for present_low_divergence in range(499,400,-1) :
      if df.loc[present_low_divergence,'하락 다이버전스?'] == 'Y' :
        print("하락 다이버전스를 찾았습니다! 위치는", present_low_divergence," 번째 입니다!")
        for find_endpoint1 in range(1,20):
          if df.loc[present_low_divergence + find_endpoint1,'하다 회수구간'] == 'Y':
            #print("하락 다이버전스가 끝났습니다.")
            break
          if find_endpoint1 + present_low_divergence == 499 and df.loc[499,'하다 회수구간'] == 'N' :
            print("현재 포지션이 없으므로 구매를 진행합니다.")

            # 구매
            order = binance.create_market_sell_order(
              symbol= what_do_you_want,
              amount= maximum_amount

              )
            print("현재시각 :", now ,"------", what_do_you_want,"를", maximum_amount,"만큼 숏을 쳤습니다!")
            
            for tictoc in range(50):
              print(tictoc,"초")
              time.sleep(1)
            break
        break


  if balance['USDT']['used'] > 0 : 
    if df.loc[499,'상다 회수구간'] == 'Y' or df.loc[498,'상다 회수구간'] == 'Y':
       #포지션 수량 찾기
      positions = balance['info']['positions']
      for position in positions:
        if position["symbol"] == what_to_buy:
          now_amount = position['positionAmt']
          now_amount = int(now_amount)


      if now_amount > 0:
        order = binance.create_market_sell_order(
        symbol= what_do_you_want,
        amount= now_amount
        )
        print(what_do_you_want,"를", now_amount,"만큼 롱포지션을 정리했습니다! 현재시간은", now ,"입니다.")
    else :
      print("아직 최대 이득구간에 도달하지 못했습니다.")



  
  if balance['USDT']['used'] == 0 : 
    for present_high_divergence in range(499,400,-1) :
      if df.loc[present_high_divergence,'상승 다이버전스?'] == 'Y' :
        print("상승 다이버전스를 찾았습니다! 위치는", present_high_divergence," 번째 입니다!")
        for find_endpoint in range(1,20):
          if df.loc[present_high_divergence + find_endpoint,'상다 회수구간'] == 'Y':
            #print("상승 다이버전스가 끝났습니다.")
            break
          if find_endpoint + present_high_divergence == 499 and df.loc[499,'상다 회수구간'] == 'N' :
            print("현재 포지션이 없으므로 구매를 진행합니다.")

            # 구매

            order = binance.create_market_buy_order(
              symbol= what_do_you_want,
              amount= maximum_amount

              )
            print("현재시각 :", now ,"------", what_do_you_want,"를", maximum_amount,"만큼 롱을 쳤습니다!")
            
            for tictoc in range(50):
              print(tictoc,"초")
              time.sleep(1)
            
            break
            
        break

  time.sleep(3)