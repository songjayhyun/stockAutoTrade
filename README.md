<h1>국내 주식 자동매매 프로그램 (Korean Stock Auto Trading Program)</h1>

이 프로그램은 국내 주식 시장에서 자동매매를 수행하는 파이썬 스크립트입니다. 해당 스크립트는 주어진 설정 파일을 기반으로 매수 및 매도 로직을 실행하여 자동으로 주식을 거래합니다.
<br><br>

<b>**기능 (Features)**</b>
- 주식 자동매매: 프로그램은 주어진 매수 목록에 따라 자동으로 매수 및 매도를 수행합니다.
- RSI 기반 매수/매도: RSI (Relative Strength Index)를 사용하여 과매수 및 과매도 상태를 판단하여 매수 또는 매도를 실행합니다.
- 디스코드 알림: 프로그램은 디스코드 웹훅을 사용하여 매수/매도 정보 및 잔고를 알립니다.
<br><br>

<b>**요구 사항 (Requirements)**</b>
- Python 3.x
- requests 라이브러리 설치
- json 라이브러리 설치
- datetime 라이브러리 설치
- time 라이브러리 설치
- yaml 라이브러리 설치
<br><br>
      
<b>**사용 방법 (Usage)**</b>
- config.yaml 파일을 생성하여 필요한 설정을 입력합니다. (APP_KEY, APP_SECRET, CANO, ACNT_PRDT_CD, DISCORD_WEBHOOK_URL, URL_BASE 등)
symbolList 변수에 매수하고자 하는 종목의 코드를 리스트 형태로 입력합니다.

<br><br>
**설정 파일 (config.yaml)**
<br>
- APP_KEY: "your_app_key_here"
- APP_SECRET: "your_app_secret_here"
- CANO: "your_cano_here"
- ACNT_PRDT_CD: "your_acnt_prdt_cd_here"
- DISCORD_WEBHOOK_URL: "your_discord_webhook_url_here"
- URL_BASE: "your_api_base_url_here"

<br><br>
**주의 사항 (Caution)**
<br>
본 프로그램은 실제 투자에 사용되기보다는 학습 및 테스트 용도로 사용되어야 합니다.
주식 자동매매에는 리스크가 있으므로 신중하게 사용하시기 바랍니다.


<br><br>
**참고 자료**
<br>
- https://www.youtube.com/watch?v=2Hxfb5HT4kE
- https://github.com/youtube-jocoding/koreainvestment-autotrade
- https://apiportal.koreainvestment.com/apiservice/oauth2#L_5c87ba63-740a-4166-93ac-803510bb9c02


