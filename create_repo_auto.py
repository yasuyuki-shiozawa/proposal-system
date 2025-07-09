#!/usr/bin/env python3
"""
GitHub リポジトリ自動作成スクリプト（非対話版）
"""

import os
import sys
import json
import subprocess
import requests

# 設定
GITHUB_USERNAME = "yasuyuki-shiozawa"
REPO_NAME = "proposal-system"
REPO_DESCRIPTION = "入札提案書作成支援システム"
PRIVATE = False

def create_github_repo():
    """GitHubリポジトリを作成"""
    
    # トークンを環境変数から取得
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("エラー: GITHUB_TOKEN環境変数が設定されていません")
        print("以下のコマンドでトークンを設定してください:")
        print('export GITHUB_TOKEN="your-token-here"')
        return False
    
    # API呼び出し
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'name': REPO_NAME,
        'description': REPO_DESCRIPTION,
        'private': PRIVATE,
        'auto_init': False
    }
    
    response = requests.post(
        'https://api.github.com/user/repos',
        headers=headers,
        json=data
    )
    
    if response.status_code == 201:
        repo_data = response.json()
        print(f"✓ リポジトリ作成成功!")
        print(f"  URL: {repo_data['html_url']}")
        print(f"  Clone URL: {repo_data['clone_url']}")
        
        # Git remote設定
        subprocess.run(['git', 'remote', 'add', 'origin', repo_data['clone_url']], check=True)
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        
        print("\n次のコマンドでプッシュしてください:")
        print("git push -u origin main")
        
        return True
    else:
        print(f"✗ リポジトリ作成失敗: {response.status_code}")
        error_data = response.json()
        print(f"  エラー: {error_data.get('message', 'Unknown error')}")
        
        if 'errors' in error_data:
            for error in error_data['errors']:
                print(f"  詳細: {error.get('message', '')}")
        
        return False

if __name__ == "__main__":
    create_github_repo()