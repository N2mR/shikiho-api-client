"""
Seleniumでスクリーニング結果を表示し、Cookieを収集する
"""

import os
import time
import json
import requests
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

try:
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
    print("\nログイン後のCookieを取得中...")
    login_cookies = driver.get_cookies()
    print(f"✓ {len(login_cookies)}個のCookieを取得しました")
    
    # スクリーニングページに遷移
    print("\nスクリーニングページに遷移中...")
    driver.get("https://shikiho.toyokeizai.net/screening")
    time.sleep(3)
    
    # スクリーニングページのCookieを取得
    print("\nスクリーニングページのCookieを取得中...")
    screening_cookies = driver.get_cookies()
    print(f"✓ {len(screening_cookies)}個のCookieを取得しました")
    
    # ページが読み込まれるまで待機
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print(f"✓ スクリーニングページに遷移しました")
    print(f"  URL: {driver.current_url}")
    
    # スクリーニング条件のリンクをクリックして別タブで結果を表示
    condition_id = "MSC0103"
    print(f"\nスクリーニング条件 {condition_id} のリンクを探しています...")
    
    link_selector = f"a[href*='{condition_id}']"
    links = driver.find_elements(By.CSS_SELECTOR, link_selector)
    
    if links:
        print(f"✓ リンクを発見しました")
        
        # リンクのURLを取得
        link_url = links[0].get_attribute('href')
        print(f"  リンク先URL: {link_url}")
        
        # 現在のウィンドウ数を記録
        initial_windows = len(driver.window_handles)
        
        # リンクをクリック
        links[0].click()
        time.sleep(2)
        
        # 新しいタブが開かれたか確認
        if len(driver.window_handles) > initial_windows:
            print("✓ 新しいタブが開かれました")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)
            
            print(f"✓ スクリーニング結果ページを表示しました")
            print(f"  URL: {driver.current_url}")
        else:
            print("✓ 同じタブで遷移しました")
            print(f"  URL: {driver.current_url}")
        
        # スクリーニング結果ページのCookieを取得
        print("\nスクリーニング結果ページのCookieを取得中...")
        result_cookies = driver.get_cookies()
        print(f"✓ {len(result_cookies)}個のCookieを取得しました")
        
        # すべてのCookieをファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        cookies_data = {
            "login_cookies": login_cookies,
            "screening_cookies": screening_cookies,
            "result_cookies": result_cookies,
            "timestamp": timestamp,
            "urls": {
                "login": "https://pa.toyokeizai.net/id/?client_id=1oC7cgjMpj",
                "screening": "https://shikiho.toyokeizai.net/screening",
                "result": driver.current_url
            }
        }
        
        filename = f"cookies_{condition_id}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cookies_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Cookieをファイルに保存しました: {filename}")
        
        # Cookie情報を表示
        print("\n=== Cookie情報 ===")
        for cookie in result_cookies:
            print(f"  {cookie['name']}: {cookie['value'][:50]}..." if len(cookie['value']) > 50 else f"  {cookie['name']}: {cookie['value']}")


        print("\nCSRFトークン取得中...")

        driver.requests.clear()

        driver.execute_script("""
            fetch('https://api-screening-shikiho.toyokeizai.net/token')
        """)

        time.sleep(2)

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
                    print(body_text)

                    data = json.loads(body_text)

                    if data.get("auth_level") == 3:
                        print("検知")
                        login_token = data
                        break

                except Exception as e:
                    print(f"トークン取得エラー: {e}")

        url = "https://api-screening-shikiho.toyokeizai.net/screening/search"

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://shikiho.toyokeizai.net",
            "referer": "https://shikiho.toyokeizai.net/",
            "user-agent": "Mozilla/5.0",
            "x-csrf-token": login_token["token"]
        }

        cookies = {c['name']: c['value'] for c in result_cookies}

        payload = {
            "filter_list": ["MF0009","MF0010","MF0011","MF0012","MF0110","MF0111","MF0112","MF0113","MF0114","MF0115"],
            "group_list": [],
            "sort_list": [{"sort_no":1,"ref_id":2,"sort_order":"desc"}],
            "srch_cond_id": "MSC0103",
            "layer_id": None,
            "srch_cond_label": "売上高を増額した銘柄",
            "relation_exp": "2 AND 3 AND 4",
            "comment": "四季報最新号比で売上高を増額修正した銘柄を抽出。ただし1億円以上増額した銘柄に限定しています",
            "result_list": [
                {"disp_flg":1,"ref_id":"MIC001"},
                {"disp_flg":1,"ref_id":"MIC004"},
                {"disp_flg":1,"ref_id":"MIC005"},
                {"disp_flg":1,"ref_id":"MI0001"}
            ],
            "cond_list": [
                {
                    "cond_id":"MC0388",
                    "lhs_id":"MI0259",
                    "rhs_list":[{"ope_id":3,"rhs_value":1}]
                }
            ],
            "auth_level": 3
        }

        res = requests.post(url, headers=headers, cookies=cookies, json=payload)
        print(res.status_code)
        print(res.text)

    else:
        print("✗ リンクが見つかりませんでした")
    
    # # ページを確認するために待機
    # print("\nページを表示中（10秒間）...")
    # time.sleep(10)

finally:
    driver.quit()
    print("\n完了")
