# Autotradebot
###### 이 코드는 개인 프로젝트로 진행하였습니다
### 목적 : 비트코인 다이버전스 탐색 후 매매를 통한 수익
### 주요 라이브러리 : ccxt, pandas
### 투자 전략 :
##### 1. RSI 및 OHLCV를 binance open api 를 통해 수집
##### 2. 다이버전스 탐색 및 다이버전스 내에서의 최고점, 최저점 탐색
##### 2-1. Binance API 로그인
##### 3. 다이버전스 이후 long or short position 잡기
##### 4. 다이버전스 내에서의 최고점, 최저점 에 도달 시 position 정리

##### - 궁금한 것이나 제안점이 있다면 말씀해주시면 감사하겠습니다
