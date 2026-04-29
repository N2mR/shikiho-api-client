import os
import time
import random
import json
import requests
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Chromeドライバーを起動
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

def login(EMAIL, PASSWORD):
    # ログイン
    print("ログイン中...")
    driver.get("https://pa.toyokeizai.net/id/?client_id=1oC7cgjMpj")
    
    email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
    email_field.send_keys(EMAIL)
    
    password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.ENTER)
    
    print("✓ ログイン完了")
    time.sleep(3)
    
    # ログイン後のCookieを取得
    login_cookies = driver.get_cookies()

    return login_cookies

# 引数のページにアクセスしCookieを取得する
def getCookies(url):
    driver.get(url)
    time.sleep(3)
    
    # スクリーニングページのCookieを取得
    cookies = driver.get_cookies()
    
    # ページが読み込まれるまで待機
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return cookies

# 認証APIからCSRFトークンを取得
def getCRFLToken():
    print("\nCSRFトークン取得中...")
    driver.requests.clear()

    # JSでHTTPリクエストを送信し、トークンをドライバで受け取る
    driver.execute_script("""
        fetch('https://api-screening-shikiho.toyokeizai.net/token', {
            method: 'GET',
            credentials: 'include'
        })
    """)
    wait.until(lambda d: any("/token" in r.url for r in d.requests))

    login_token = {}
    for request in driver.requests:
        if "/token" in request.url and request.response:
            try:
                import gzip
                import json
                body = request.response.body

                # gzip判定
                if body[:2] == b'\x1f\x8b':
                    body = gzip.decompress(body)

                body_text = body.decode('utf-8')
                
                # body_textがJSON形式の場合のみ
                if body_text.startswith("{"):
                    data = json.loads(body_text)
                    if data.get("auth_level") == 3: # 3はログイン済を意味する
                        print("✓ CSRFトークン取得")
                        return data.get("token")
                else:
                    continue
            except Exception as e:
                print(f"トークン取得エラー: {e}")
    
    return None 

# スクリーニングに必要なペイロードを取得(リクエストヘッダーに付加する)
def getPayloadByConditionID(condition_id):
    # 条件データを取得
    condition_url = f"https://api-screening-shikiho.toyokeizai.net/screening/srchcond/{condition_id}"
    condition_res = requests.get(condition_url, headers=HEADERS, cookies=cookies)
    return condition_res.json() if condition_res.status_code == 200 else ""

# スクリーニング実行
def execScreening(payload):
    # 検索APIを実行
    print("\nスクリーニング検索を実行中...")
    search_url = "https://api-screening-shikiho.toyokeizai.net/screening/search"
    
    # 取得した条件データをそのまま使用
    search_res = requests.post(search_url, headers=HEADERS, cookies=cookies, json=payload)
    
    print(f"\n検索結果:")
    print(f"ステータスコード: {search_res.status_code}")

    return search_res.json()
    
# 銘柄コードをキーに情報取得
def getStockDataByID(id, headers, cookies):
    getStockData_url = f"https://api-shikiho.toyokeizai.net/stocks/v1/stocks/{id}/latest"

    getStockData_res = requests.get(getStockData_url, headers=headers, cookies=cookies)
    time.sleep(random.uniform(0.2, 0.6))
    return json.loads(getStockData_res.text)

# 銘柄データは不要な情報が多すぎるためフォーマット
def formatStockData(stockData):
    ret = stockData.copy()

    # 不要キー削除
    keys_to_remove = [
        "profitability_list",
        "modified_forecasts_list",
        "modified_forecasts_list_company",
        "shimen_results",
        "shimen_dividends",
        "shimen_finances",
        "shimen_stats",
        "shimen_cfs",
        "shimen_underwriters",
        "shimen_banks",
        "shimen_vendors",
        "shimen_customers",
        "shimen_recruit",
    ]

    for key in keys_to_remove:
        ret.pop(key, None)

    # growth_potential_list を軽量化
    growth_list = ret.get("growth_potential_list", [])

    ret["growth_potential_list"] = [
        {
            "year": x.get("year"),
            "sales_growth": x.get("sales_growth"),
            "ope_growth": x.get("ope_growth"),
            "ord_growth": x.get("ord_growth"),
        }
        for x in growth_list
        if (
            x.get("sales_growth") not in [None, "ー"]
            or x.get("ope_growth") not in [None, "ー"]
            or x.get("ord_growth") not in [None, "ー"]
        )
    ]

    return ret

try:
    # 実行時タイムスタンプ
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # .evnファイル定義のユーザ情報でログイン
    login_cookies = login(EMAIL, PASSWORD)
    
    # スクリーニング方式の一覧からリダイレクトするためcookieを取得しておく
    screening_cookies = getCookies("https://shikiho.toyokeizai.net/screening")
    
    # スクリーニング実行にCRLFトークンが必要
    crlf_token = getCRFLToken()
    if not crlf_token:
        raise RuntimeError("CRLFトークン取得失敗")
    
    # ログイン後にcookieを更新
    cookies = {}
    cookies.update({c['name']: c['value'] for c in login_cookies})
    cookies.update({c['name']: c['value'] for c in screening_cookies})
    
    # リクエストヘッダー定義
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://shikiho.toyokeizai.net",
        "referer": "https://shikiho.toyokeizai.net/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-csrf-token": crlf_token
    }

    # スクリーニングメソッドのID（オンライン四季報定義）
    CONDITION_ID = "MSC0103"
    
    # スクリーニング実行
    condition_data = getPayloadByConditionID(CONDITION_ID)
    search_result = execScreening(condition_data)

    output_data = []
    for obj in tqdm(search_result["data"]["results"]):
        code = obj[1]
        name = obj[3]

        if code and name:
            stock_data = getStockDataByID(code, HEADERS, cookies)
            if stock_data:
                formatted_stock_data = formatStockData(stock_data)
                output_data.append(formatted_stock_data)    
    
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump({"data": output_data}, f, ensure_ascii=False)


finally:
    driver.quit()
    print("\n完了")
