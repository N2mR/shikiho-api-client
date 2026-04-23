"""
四季報APIクライアント - セッション管理モジュール

Seleniumで取得したクッキーをrequestsセッションに変換し、
API呼び出しに使用できるようにします。
"""

import requests


def create_session(cookies):
    """
    Seleniumから取得したクッキーをrequestsセッションに変換する
    
    Args:
        cookies (list): Seleniumのget_cookies()で取得したクッキーリスト
                       各クッキーは辞書形式で、name, value, domain, pathなどを含む
    
    Returns:
        requests.Session: クッキーが設定されたセッションオブジェクト
    
    Note:
        このヘルパー関数は、main.pyで直接クッキーを設定する方法に置き換えられました。
        互換性のために残していますが、新しいコードではmain.pyのパターンを使用してください。
    """
    session = requests.Session()
    
    for cookie in cookies:
        domain = cookie.get("domain")
        
        # toyokeizai.netドメインの場合、サブドメイン間で共有できるように調整
        if domain and "toyokeizai.net" in domain:
            domain = ".toyokeizai.net"
        
        session.cookies.set(
            name=cookie['name'],
            value=cookie['value'],
            domain=domain,
            path=cookie.get('path', '/')
        )
    
    return session
