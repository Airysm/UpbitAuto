from BitcoinAutoTrade_module import *
import pyupbit
import time
import datetime

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

access = "###############################"                     # upbit access key
secret = "###############################"                     # upbit secret key
myToken = "################################"   # slack bot token

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#bitcoin", "autotrade start")
# 변동성 돌파 전략 k값
k_value = 0.55

# 자동매매 시작
i=0 # 전략값 갱신 키 : i
buyed=[] # 구매한 비트코인 list
while True:
    try:
        # 비트코인 시간
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC") #9:00
        end_time = start_time + datetime.timedelta(days=1) #9:00 + 1일

        # 9:00:02 시간에 전략값 갱신
        if now == start_time+datetime.timedelta(seconds=2):
            i=0

        # 9:00 < 현재 < 다음날 8:59:50
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            # else 갱신 키 : j
            j=0
            # 전략값
            if i==0:
                # 변동성 돌파 전략 list
                target_prices = []
                for bitcoin in pyupbit.get_tickers():
                    if bitcoin[0] == 'K' and bitcoin[1] == 'R' and bitcoin[2] == 'W':
                        target_prices.append(get_target_price(bitcoin, k_value))
                        time.sleep(0.1)

                # 이동평균선 15일 list
                ma15 = []
                for bitcoin in pyupbit.get_tickers():
                    if bitcoin[0] == 'K' and bitcoin[1] == 'R' and bitcoin[2] == 'W':
                        ma15.append(get_ma15(bitcoin))
                        time.sleep(0.1)
                i=1
            # 매수 작업
            count=0
            for bitcoin in pyupbit.get_tickers():
                if bitcoin[0] == 'K' and bitcoin[1] == 'R' and bitcoin[2] == 'W':
                    current_price = get_current_price(bitcoin)
                    if target_prices[count] < current_price and ma15[count] < current_price:
                        if bitcoin not in buyed:
                            buyed.append(bitcoin)
                            krw = get_balance("KRW")
                            if krw > 5000:
                                #buy_result = upbit.buy_market_order(bitcoin, 5000)
                                print("buy : ", bitcoin)  # 다음날 9시에 해보자 이거 지우셈
                                buy_result =0             #2222
                                post_message(myToken, "#bitcoin", bitcoin + " buy : " + str(buy_result))
                    count = count + 1
                    time.sleep(0.1)
        else:
            if j==0:
                before_balance = get_balance("KRW")
                # 매도 작업
                for bitcoin in buyed:
                    btc = get_balance(bitcoin) # 구매한 비트코인
                    #sell_result = upbit.sell_market_order(bitcoin, btc * 0.9995)
                    print("sell : ", bitcoin) # 다음날 지우자
                    sell_result =0            #2222
                    post_message(myToken, "#bitcoin", "ETH buy : " + str(sell_result))
                    time.sleep(1)

                # 수익률 계산
                after_balance = get_balance("KRW")
                stock_returns = (after_balance-before_balance) / before_balance * 100
                post_message(myToken, "#bitcoin", "수익률 : " + str(stock_returns) + "%")
                # 구매한 비트코인 list 초기화
                buyed = []

                j=1
    except Exception as e:
        print(e)
        post_message(myToken, "#bitcoin", e)
        time.sleep(1)