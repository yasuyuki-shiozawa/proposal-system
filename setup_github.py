#!/usr/bin/env python3
"""GitHubリポジトリ作成とプッシュ"""
import subprocess
import sys
import os

print("=== GitHub セットアップ ===\n")

# トークンを環境変数から読み取る
token = os.environ.get('GITHUB_TOKEN', '')

if not token:
    print("エラー: GITHUB_TOKENが設定されていません")
    print("\n以下のコマンドを実行してください:")
    print("set GITHUB_TOKEN=あなたのトークン")
    print("python setup_github.py")
    sys.exit(1)

# GitHubリポジトリ作成
import requests

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

data = {
    'name': 'proposal-system',
    'description': '入札提案書作成支援システム',
    'private': False
}

print("リポジトリを作成中...")
response = requests.post(
    'https://api.github.com/user/repos',
    headers=headers,
    json=data
)

if response.status_code == 201:
    print("✓ リポジトリ作成成功!")
    repo_url = response.json()['clone_url']
    
    # Git設定とプッシュ
    commands = [
        f"git remote add origin {repo_url}",
        "git push -u origin main"
    ]
    
    for cmd in commands:
        print(f"\n実行: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 成功")
        else:
            print(f"✗ エラー: {result.stderr}")
            
elif response.status_code == 422:
    print("リポジトリは既に存在します。プッシュを試みます...")
    repo_url = f"https://github.com/yasuyuki-shiozawa/proposal-system.git"
    subprocess.run(f"git remote add origin {repo_url}", shell=True)
    subprocess.run("git push -u origin main", shell=True)
else:
    print(f"エラー: {response.status_code}")
    print(response.json())