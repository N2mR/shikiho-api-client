# 四季報APIクライアント

東洋経済の四季報APIにアクセスするためのPythonクライアントライブラリです。

## 機能

- 自動ログインとセッション確立
- スクリーニング条件の取得
- スクリーニングの実行
- CSRF トークンの自動生成

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install python-dotenv selenium requests
```

### 2. 環境変数の設定

`.env`ファイルを作成し、ログイン情報を設定します：

```
EMAIL=your-email@example.com
PASSWORD=your-password
```

## 基本的な使い方

### セッションの確立

```python
from main import main

# ログインしてセッションを確立
session = main()
```

### スクリーニング条件の取得

```python
from screening import get_screening_condition

# スクリーニング条件を取得
condition = get_screening_condition(session, "MSC0004")
print(condition)
```

### スクリーニングの実行

```python
from screening import execute_screening

# デフォルト条件でスクリーニング実行
result = execute_screening(session)
print(f"取得件数: {len(result.get('data', []))}")

# カスタム条件でスクリーニング実行
custom_filters = ["MF0009", "MF0010", "MF0012"]
result = execute_screening(
    session,
    filter_list=custom_filters,
    srch_cond_id="MSC0082"
)
```

## サンプルスクリプト

`example_screening.py`に使用例が含まれています：

```bash
python example_screening.py
```

## ファイル構成

- `main.py` - メインスクリプト（セッション確立）
- `login.py` - ログイン処理
- `client.py` - セッション管理ヘルパー
- `screening.py` - スクリーニングAPI関数
- `example_screening.py` - 使用例

## 注意事項

### 403 Forbiddenエラーについて

スクリーニングAPIは、適切なクッキーとCSRFトークンが必要です。以下の点を確認してください：

1. **セッションの確立**: `main()`を実行してセッションを確立してください
2. **api-session-id**: ログインフローで自動的に取得されます
3. **CSRFトークン**: 各リクエストで自動生成されます

現在、スクリーニング条件の取得（GET）とスクリーニング実行（POST）で403エラーが発生する場合があります。これは以下の理由が考えられます：

- クッキーのドメイン設定の問題
- 追加の認証ヘッダーが必要
- セッションの有効期限

### トラブルシューティング

1. **ログインに失敗する場合**
   - `.env`ファイルの認証情報を確認
   - ChromeDriverのバージョンを確認

2. **403エラーが発生する場合**
   - セッションが正しく確立されているか確認
   - ブラウザで手動ログインして、開発者ツールでリクエストヘッダーを確認

## ライセンス

このプロジェクトは個人利用を目的としています。
