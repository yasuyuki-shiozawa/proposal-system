# Claude Code への指示書：GitHub リポジトリ作成とプッシュ

## 概要
このプロジェクト（proposal-system）をGitHubにアップロードするための指示書です。

## 手順

### 1. プロジェクトディレクトリに移動
```
cd /mnt/c/Users/shioz/Downloads/proposal-system
```

### 2. 現在の状態を確認
```
git status
git log --oneline -1
```

### 3. GitHubリポジトリの作成

以下の情報でGitHubリポジトリを作成してください：
- **ユーザー名**: yasuyuki-shiozawa
- **リポジトリ名**: proposal-system
- **説明**: 入札提案書作成支援システム
- **公開/非公開**: 公開（Public）

### 4. Personal Access Token の設定

GitHubのPersonal Access Tokenを使用してリポジトリを作成します。

```bash
# トークンを環境変数に設定
export GITHUB_TOKEN="[ここにPersonal Access Tokenを入力]"

# curlでリポジトリ作成
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "proposal-system",
    "description": "入札提案書作成支援システム",
    "private": false
  }'
```

### 5. リモートリポジトリの設定

リポジトリ作成が成功したら：

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/yasuyuki-shiozawa/proposal-system.git

# ブランチ名をmainに設定（念のため）
git branch -M main

# リモート設定を確認
git remote -v
```

### 6. 初回プッシュ

```bash
# GitHubにプッシュ
git push -u origin main
```

### 7. 確認

プッシュ成功後、以下のURLでリポジトリを確認：
https://github.com/yasuyuki-shiozawa/proposal-system

## エラー対処

### リポジトリが既に存在する場合
```bash
# 既存のリポジトリを使用
git remote add origin https://github.com/yasuyuki-shiozawa/proposal-system.git
git push -u origin main --force
```

### 認証エラーの場合
1. Personal Access Tokenが正しいか確認
2. トークンに「repo」権限があるか確認
3. トークンの期限が切れていないか確認

### プッシュが拒否される場合
```bash
# 強制プッシュ（注意：既存の内容を上書きします）
git push -u origin main --force
```

## 完了後の作業

1. **README.mdの確認**
   - プロジェクトの説明が適切か確認

2. **requirements.txtの確認**
   - 必要なパッケージがすべて含まれているか確認

3. **Streamlitアプリの動作確認**
   ```bash
   pip install -r requirements.txt
   streamlit run streamlit_app.py
   ```

## 注意事項

- Personal Access Tokenは絶対に他人と共有しない
- トークンをファイルに保存する場合は `.env` ファイルを使用し、`.gitignore` に追加する
- 公開リポジトリの場合、機密情報が含まれていないか必ず確認する

---

## コピペ用コマンド集

すべてを一度に実行する場合：

```bash
cd /mnt/c/Users/shioz/Downloads/proposal-system
export GITHUB_TOKEN="YOUR_TOKEN_HERE"
curl -X POST -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github.v3+json" https://api.github.com/user/repos -d '{"name": "proposal-system", "description": "入札提案書作成支援システム", "private": false}'
git remote add origin https://github.com/yasuyuki-shiozawa/proposal-system.git
git branch -M main
git push -u origin main
```

Personal Access Tokenを「YOUR_TOKEN_HERE」の部分に置き換えて実行してください。