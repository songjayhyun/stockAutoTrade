import requests
import json
import datetime
import time
import yaml

with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
URL_BASE = _cfg['URL_BASE']

def sendDiscordMsg(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)

def generateToken():
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    
    headers = {
        "content-type":"application/json"
    }
    body = {
        "grant_type":"client_credentials",
        "appkey": APP_KEY, 
        "appsecret": APP_SECRET
    } 
    
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    return res.json()["access_token"]
    
def generateHashkey(datas):
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"

    headers = {
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010100"
    }

    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    return res.json()["HASH"]

def getCurrentPrice(code):
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"

    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id":"FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code":"J",
        "fid_input_iscd":code
    } 
    
    res = requests.get(URL, headers=headers, params=params)
    return int(res.json()['output']['stck_prpr'])

def calcualateRsi(prices, period=2):
    changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    ups = [change for change in changes if change > 0]
    downs = [-change for change in changes if change < 0]

    avg_up = sum(ups[-period:]) / period
    avg_down = sum(downs[-period:]) / period

    rs = avg_up / avg_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

def getTargetPrices(code):
    
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    
    headers = {
        "Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"
    }
    params = {
        "fid_cond_mrkt_div_code":"J",
        "fid_input_iscd":code,
        "fid_org_adj_prc":"1",
        "fid_period_div_code":"D"
    }

    res = requests.get(URL, headers=headers, params=params)
    stck_oprc = int(res.json()['output'][0]['stck_oprc']) #오늘 시가
    stck_hgpr = int(res.json()['output'][1]['stck_clpr']) #전일 종가
    
    prices = []
    prices.append(stck_oprc)
    prices.append(stck_hgpr)
    
    return prices

def getStockBalance():
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"

    headers = {
        "Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8434R",
        "custtype":"P"
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    
    res = requests.get(URL, headers=headers, params=params)
    stock_list = res.json()['output1']
    stockDict = {}
    for stock in stock_list:
        if int(stock['hldg_qty']) > 0:
            stockDict[stock['pdno']] = stock['hldg_qty']
            time.sleep(0.1)

    return stockDict

def notifyCurrentBalance():
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"

    headers = {
        "Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8434R",
        "custtype":"P"
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "", 
        "CTX_AREA_NK100": ""
    }
    
    res = requests.get(URL, headers=headers, params=params)
    stock_list = res.json()['output1']
    evaluation = res.json()['output2']
    stockDict = {}
    sendDiscordMsg(f"====주식 보유잔고====")
    for stock in stock_list:
        if int(stock['hldg_qty']) > 0:
            stockDict[stock['pdno']] = stock['hldg_qty']
            sendDiscordMsg(f"{stock['prdt_name']}({stock['pdno']}): {stock['hldg_qty']}주")
            time.sleep(0.1)
    sendDiscordMsg(f"주식 평가 금액: {evaluation[0]['scts_evlu_amt']}원")
    time.sleep(0.1)
    sendDiscordMsg(f"평가 손익 합계: {evaluation[0]['evlu_pfls_smtl_amt']}원")
    time.sleep(0.1)
    sendDiscordMsg(f"총 평가 금액: {evaluation[0]['tot_evlu_amt']}원")
    time.sleep(0.1)
    sendDiscordMsg(f"=================")

def getBalance():
    PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
    URL = f"{URL_BASE}/{PATH}"

    headers = {
        "Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8908R",
        "custtype":"P"
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": "005930",
        "ORD_UNPR": "65500",
        "ORD_DVSN": "01",
        "CMA_EVLU_AMT_ICLD_YN": "Y",
        "OVRS_ICLD_YN": "Y"
    }
    
    res = requests.get(URL, headers=headers, params=params)
    cash = res.json()['output']['ord_psbl_cash']

    sendDiscordMsg(f"주문 가능 현금 잔고: {cash}원")

    return int(cash)

def buyStock(code, qty):
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"

    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id":"TTTC0802U",
        "hashkey" : generateHashkey(data)
    }
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(qty)),
        "ORD_UNPR": "0"
    }
    
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        sendDiscordMsg(f"[매수 성공]{str(res.json())}")
        return True
    else:
        sendDiscordMsg(f"[매수 실패]{str(res.json())}")
        return False

def sellStock(code, qty):
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"

    headers = {
        "Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC0801U",
        "custtype":"P",
        "hashkey" : generateHashkey(data)
    }
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": qty,
        "ORD_UNPR": "0"
    }

    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        sendDiscordMsg(f"[매도 성공]{str(res.json())}")
        return True
    else:
        sendDiscordMsg(f"[매도 실패]{str(res.json())}")
        return False

# 자동매매 시작
try:
    ACCESS_TOKEN = generateToken()

    symbolList = ["005930","035720","000660"] # 매수 희망 종목 리스트
    stockDict = getStockBalance() # 보유 주식 조회
    totalCash = getBalance() # 보유 현금 조회
    
    boughtList = [] # 매수 완료된 종목 리스트
    for sym in stockDict.keys():
        boughtList.append(sym)

    targetBuyCount = 3 # 매수할 종목 수
    buyPercent = 0.33 # 종목당 매수 금액 비율
    buyAmount = totalCash * buyPercent  # 종목별 주문 금액 계산
    soldOut = False
    overbought_threshold = 70
    oversold_threshold = 30

    sendDiscordMsg("===국내 주식 자동매매 프로그램을 시작합니다===")
    while True:
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()

        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            sendDiscordMsg("주말이므로 프로그램을 종료합니다.")
            break

        if t_9 < t_now < t_start and soldOut == False: # 잔여 수량 매도
            for sym, qty in stockDict.items():
                sellStock(sym, qty)
            soldOut == True
            boughtList = []
            stockDict = getStockBalance()
            notifyCurrentBalance()

        if t_start < t_now < t_sell :  # AM 09:05 ~ PM 03:15 : 매수
            for sym in symbolList:
                currentPrice = getCurrentPrice(sym)
                prices = getTargetPrices(sym)
                rsi = calcualateRsi(prices, 2) ## 현재 period는 2일

                if len(boughtList) < targetBuyCount:
                    if sym in boughtList:
                        continue

                    if rsi >= overbought_threshold: # RSI가 70 이상이면 과매수 상태로 매도
                        buy_qty = 0  # 매수할 수량 초기화
                        buy_qty = int(buyAmount // currentPrice)
                        if buy_qty > 0:
                            sendDiscordMsg(f"{sym} 매수를 시도합니다.")
                            result = buyStock(sym, buy_qty)
                            if result:
                                soldOut = False
                                boughtList.append(sym)
                                getStockBalance()
                                notifyCurrentBalance()
                    time.sleep(1)

                if rsi <= oversold_threshold: # RSI가 30 이하이면 과매도 상태로 매수
                    if soldOut == False:
                        stockDict = getStockBalance()
                        sellStock(sym, stockDict[sym])
                    soldOut = True
                    boughtList.remove(sym)
                    time.sleep(1)
                notifyCurrentBalance()
                
            time.sleep(1)
            
            if t_now.minute == 30 and t_now.second <= 5: 
                getStockBalance()
                notifyCurrentBalance()
                time.sleep(5)

        if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
            if soldOut == False:
                stockDict = getStockBalance()
                for sym, qty in stockDict.items():
                    sellStock(sym, qty)
                soldOut = True
                boughtList = []
                time.sleep(1)
            notifyCurrentBalance()

        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            sendDiscordMsg("프로그램을 종료합니다.")
            break

except Exception as e:
    sendDiscordMsg(f"[오류 발생]{e}")
    time.sleep(1)