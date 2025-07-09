#!/bin/bash

# GitHubリポジトリ作成スクリプト

GITHUB_USERNAME="yasuyuki-shiozawa"
REPO_NAME="proposal-system"
REPO_DESCRIPTION="入札提案書作成支援システム"

echo "=== GitHub リポジトリ作成 ==="
echo ""

# トークンの確認
if [ -z "$GITHUB_TOKEN" ]; then
    echo "エラー: GITHUB_TOKEN環境変数が設定されていません"
    echo ""
    echo "以下の手順でトークンを設定してください:"
    echo "1. 新しいターミナルで以下を実行:"
    echo '   export GITHUB_TOKEN="your-personal-access-token"'
    echo ""
    echo "2. その後、このスクリプトを再実行:"
    echo "   ./create_repo.sh"
    exit 1
fi

echo "リポジトリを作成中..."

# GitHub API呼び出し
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\": \"$REPO_NAME\",
    \"description\": \"$REPO_DESCRIPTION\",
    \"private\": false
  }")

# レスポンスの解析
BODY=$(echo "$RESPONSE" | sed '$d')
STATUS_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$STATUS_CODE" = "201" ]; then
    echo "✓ リポジトリ作成成功!"
    
    # URLの取得
    HTML_URL=$(echo "$BODY" | grep -o '"html_url":"[^"]*' | grep -o 'https://github.com/[^"]*' | head -1)
    CLONE_URL=$(echo "$BODY" | grep -o '"clone_url":"[^"]*' | grep -o 'https://github.com/[^"]*\.git')
    
    echo "  URL: $HTML_URL"
    echo "  Clone URL: $CLONE_URL"
    echo ""
    
    # Git remote設定
    echo "Git remoteを設定中..."
    git remote add origin "$CLONE_URL"
    git branch -M main
    
    echo ""
    echo "✓ 設定完了!"
    echo ""
    echo "次のコマンドでコードをプッシュしてください:"
    echo "  git push -u origin main"
    
elif [ "$STATUS_CODE" = "422" ]; then
    echo "✗ エラー: リポジトリ '$REPO_NAME' は既に存在します"
    echo ""
    echo "以下のいずれかを実行してください:"
    echo "1. 既存のリポジトリを使用:"
    echo "   git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "   git push -u origin main"
    echo ""
    echo "2. 別の名前でリポジトリを作成"
else
    echo "✗ リポジトリ作成失敗 (HTTP $STATUS_CODE)"
    echo "$BODY" | grep -o '"message":"[^"]*' | cut -d'"' -f4
fi