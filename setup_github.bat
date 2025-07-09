@echo off
echo === GitHub リポジトリセットアップ ===
echo.

echo GitHubのPersonal Access Tokenを入力してください:
echo (トークンは画面に表示されません)
echo.

set /p GITHUB_TOKEN=トークン: 

echo.
echo トークンを設定しました。リポジトリを作成します...
echo.

REM Windows用のcurlコマンドでリポジトリ作成
curl -X POST ^
  -H "Authorization: token %GITHUB_TOKEN%" ^
  -H "Accept: application/vnd.github.v3+json" ^
  https://api.github.com/user/repos ^
  -d "{\"name\": \"proposal-system\", \"description\": \"入札提案書作成支援システム\", \"private\": false}"

echo.
echo.

REM Git設定
git remote add origin https://github.com/yasuyuki-shiozawa/proposal-system.git
git branch -M main

echo.
echo 準備完了！以下のコマンドでプッシュしてください:
echo   git push -u origin main
echo.

pause