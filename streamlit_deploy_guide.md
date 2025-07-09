# Streamlit Cloud デプロイガイド

## 手順

### 1. Streamlit Cloudにアクセス
https://share.streamlit.io/

### 2. サインイン
「Sign in with GitHub」をクリック（すでにログイン済みならスキップ）

### 3. 新しいアプリを作成
「New app」ボタンをクリック

### 4. リポジトリ情報を入力
- **Repository**: yasuyuki-shiozawa/proposal-system
- **Branch**: main
- **Main file path**: streamlit_app.py

### 5. Advanced settings（オプション）
- **Python version**: 3.9（推奨）
- **App URL**: カスタムURL（例: proposal-yasuyuki）
  - 最終URL: https://proposal-yasuyuki.streamlit.app

### 6. Deploy!
「Deploy!」ボタンをクリック

## デプロイ状況
- 初回は3-5分かかります
- ログが表示され、進行状況を確認できます
- エラーがあれば赤く表示されます

## 完成後
- URLが表示されます
- そのURLを共有すれば誰でもアクセス可能
- GitHubにプッシュすると自動的に更新されます

## トラブルシューティング

### よくあるエラー
1. **ModuleNotFoundError**
   - requirements.txtの確認
   - パッケージ名のスペルミス

2. **Port already in use**
   - Streamlit側の問題、少し待って再試行

3. **Build failed**
   - ログを確認して原因を特定