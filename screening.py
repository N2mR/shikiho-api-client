"""
四季報APIクライアント - スクリーニングモジュール

四季報のスクリーニングAPIを呼び出して、
条件に合致する銘柄データを取得します。
"""

import uuid

API_BASE_URL = "https://api-screening-shikiho.toyokeizai.net"
SCREENING_SEARCH_URL = f"{API_BASE_URL}/screening/search"
SCREENING_CONDITION_URL = f"{API_BASE_URL}/screening/srchcond"


def get_screening_condition(session, condition_id="MSC0004"):
    """
    スクリーニング条件の詳細を取得する
    
    Args:
        session (requests.Session): 認証済みのセッションオブジェクト
        condition_id (str, optional): 検索条件ID。デフォルトは"MSC0004"
    
    Returns:
        dict: スクリーニング条件の詳細情報
        
    Raises:
        Exception: API呼び出しが失敗した場合
    
    Example:
        >>> session = main()
        >>> condition = get_screening_condition(session, "MSC0004")
        >>> print(condition)
    """
    
    # CSRF トークンを取得（skolp_tokenクッキーから、なければUUID生成）
    csrf_token = None
    for cookie in session.cookies:
        if cookie.name == "skolp_token":
            csrf_token = cookie.value
            break
    if not csrf_token:
        csrf_token = str(uuid.uuid4())
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ja,en-US;q=0.9,en;q=0.8",
        "origin": "https://shikiho.toyokeizai.net",
        "referer": "https://shikiho.toyokeizai.net/screening",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token
    }
    
    url = f"{SCREENING_CONDITION_URL}/{condition_id}"
    response = session.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(
            f"スクリーニング条件取得失敗: "
            f"ステータスコード {response.status_code}, "
            f"レスポンス: {response.text}"
        )
    
    return response.json()


def execute_screening(session, filter_list=None, group_list=None, srch_cond_id="MSC0082"):
    """
    スクリーニングAPIを実行して銘柄データを取得する
    
    Args:
        session (requests.Session): 認証済みのセッションオブジェクト
        filter_list (list, optional): フィルター条件のリスト
        group_list (list, optional): グループ条件のリスト
        srch_cond_id (str, optional): 検索条件ID。デフォルトは"MSC0082"
    
    Returns:
        dict: スクリーニング結果のJSON
        
    Raises:
        Exception: API呼び出しが失敗した場合
    
    Example:
        >>> session = main()
        >>> result = execute_screening(session)
        >>> print(f"取得件数: {len(result.get('data', []))}")
    """
    
    # デフォルトのフィルター条件
    if filter_list is None:
        filter_list = [
            "MF0009",  # 時価総額
            "MF0010",  # PER
            "MF0011",  # PBR
            "MF0012",  # 配当利回り
            "MF0110",  # ROE
            "MF0111",  # ROA
            "MF0112",  # 自己資本比率
            "MF0113",  # 営業利益率
            "MF0114",  # 売上高成長率
            "MF0115"   # 営業利益成長率
        ]
    
    if group_list is None:
        group_list = []
    
    # CSRF トークンを取得（skolp_tokenクッキーから、なければUUID生成）
    csrf_token = None
    for cookie in session.cookies:
        if cookie.name == "skolp_token":
            csrf_token = cookie.value
            break
    if not csrf_token:
        csrf_token = str(uuid.uuid4())
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ja,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://shikiho.toyokeizai.net",
        "referer": "https://shikiho.toyokeizai.net/screening",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token
    }
    
    payload = {
        "filter_list": filter_list,
        "group_list": group_list,
        "srch_cond_id": srch_cond_id
    }
    
    response = session.post(SCREENING_SEARCH_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(
            f"スクリーニングAPI呼び出し失敗: "
            f"ステータスコード {response.status_code}, "
            f"レスポンス: {response.text}"
        )
    
    return response.json()
