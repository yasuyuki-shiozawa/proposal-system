@echo off
echo === GitHub Setup ===
echo.
echo 1. トークンを環境変数に設定します
echo 2. Pythonスクリプトを実行します
echo.
echo 準備ができたらEnterキーを押してください...
pause >nul

pip install requests
python setup_github.py

echo.
echo 完了しました！
pause