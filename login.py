"""
四季報APIクライアント - ログインモジュール

Seleniumを使用して東洋経済の四季報サイトにログインし、
API認証に必要なクッキーを取得します。
"""

import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# def login_and_get_cookies():
#     """
#     基本的なログインフローでクッキーを取得する
    
#     Returns:
#         list: Seleniumから取得したクッキーのリスト
#     """
#     load_dotenv()
    
#     EMAIL = os.getenv("EMAIL")
#     PASSWORD = os.getenv("PASSWORD")
    
#     driver = webdriver.Chrome()
#     wait = WebDriverWait(driver, 10)
    
#     try:
#         # ログインページにアクセス
#         driver.get("https://pa.toyokeizai.net/id/?client_id=1oC7cgjMpj")
        
#         # 認証情報を入力
#         email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
#         email_field.send_keys(EMAIL)
        
#         password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
#         password_field.send_keys(PASSWORD)
#         password_field.send_keys(Keys.ENTER)
        
#         # ログイン完了を待機
#         time.sleep(3)
        
#         # 四季報サイトに遷移
#         driver.get("https://shikiho.toyokeizai.net")
#         time.sleep(1)  # ページ読み込み待機
        
#         # APIドメインにアクセスしてセッションを確立
#         driver.get("https://api-shikiho.toyokeizai.net/")
#         time.sleep(1)  # クッキー設定待機
        
#         # クッキーを取得
#         cookies = driver.get_cookies()
        
#         return cookies
        
#     finally:
#         driver.quit()


def login_and_get_api_session():
    """
    APIセッション確立用のログインフロー
    
    このフローでは、以下のステップを実行します：
    1. ログインページで認証
    2. 四季報トップページに遷移
    3. スクリーニングページに遷移（APIセッション生成のトリガー）
    4. APIエンドポイントに直接アクセスしてセッション確立
    5. スクリーニングAPIドメインにもアクセス
    
    Returns:
        list: 認証済みクッキーのリスト（ドメイン情報を含む）
        
    Raises:
        Exception: api-session-idクッキーが取得できなかった場合
    """
    load_dotenv()
    
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    try:
        # ステップ1: ログインページで認証
        driver.get("https://pa.toyokeizai.net/id/?client_id=1oC7cgjMpj")
        
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        email_field.send_keys(EMAIL)
        
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.ENTER)
        
        # ログイン完了を待機
        time.sleep(3)
        
        # ステップ2: 四季報トップページに遷移
        driver.get("https://shikiho.toyokeizai.net")
        time.sleep(1)  # ページ読み込み待機
        
        # ステップ3: スクリーニングページに遷移（APIセッション生成）
        driver.get("https://shikiho.toyokeizai.net/screening")
        time.sleep(2)  # APIセッション生成待機
        
        # ステップ4: APIエンドポイントに直接アクセスしてセッション確立
        driver.get("https://api-shikiho.toyokeizai.net/sso/v1/sso/check")
        time.sleep(1)  # セッション確立待機
        
        # ステップ5: スクリーニングAPIドメインにもアクセス
        driver.get("https://api-screening-shikiho.toyokeizai.net/")
        time.sleep(1)  # クッキー設定待機
        
        # クッキーを取得
        cookies = driver.get_cookies()
        
        # api-session-idの存在を確認
        cookie_dict = {c['name']: c['value'] for c in cookies}
        api_session_id = cookie_dict.get("api-session-id")
        
        if not api_session_id:
            raise Exception(
                "api-session-idクッキーが取得できませんでした。"
                "ログインフローを確認してください。"
            )
        
        return cookies
        
    finally:
        driver.quit()
