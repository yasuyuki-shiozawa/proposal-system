#!/usr/bin/env python3
"""
GitHub リポジトリ自動作成スクリプト
安全にトークンを管理しながらリポジトリを作成します
"""

import os
import sys
import json
import getpass
import subprocess
from pathlib import Path
import requests

class GitHubRepoCreator:
    def __init__(self):
        self.api_base = "https://api.github.com"
        self.username = "yasuyuki-shiozawa"
        self.token = None
        
    def get_token_safely(self):
        """トークンを安全に取得"""
        print("GitHubパーソナルアクセストークンが必要です。")
        print("\n取得方法:")
        print("1. https://github.com/settings/tokens にアクセス")
        print("2. 'Generate new token (classic)' をクリック")
        print("3. 'repo' にチェックを入れる")
        print("4. 'Generate token' をクリック")
        print("\n注意: トークンは画面に表示されません（セキュリティのため）")
        
        # 環境変数から取得を試みる
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            print("✓ 環境変数からトークンを検出しました")
            return token
            
        # 手動入力
        token = getpass.getpass("\nトークンを貼り付けてEnter: ")
        
        # 一時的に環境変数に保存（このセッションのみ）
        os.environ['GITHUB_TOKEN'] = token
        
        return token
        
    def verify_token(self, token):
        """トークンの有効性を確認"""
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(f"{self.api_base}/user", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ 認証成功: {user_data['login']}")
            return True
        else:
            print(f"✗ 認証失敗: {response.status_code}")
            return False
            
    def create_repository(self, repo_name, description, private=False):
        """リポジトリを作成"""
        if not self.token:
            self.token = self.get_token_safely()
            
        if not self.verify_token(self.token):
            print("トークンが無効です。")
            return False
            
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'name': repo_name,
            'description': description,
            'private': private,
            'auto_init': False
        }
        
        response = requests.post(
            f"{self.api_base}/user/repos",
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            repo_data = response.json()
            print(f"\n✓ リポジトリ作成成功!")
            print(f"  URL: {repo_data['html_url']}")
            print(f"  Clone URL: {repo_data['clone_url']}")
            return repo_data
        else:
            print(f"\n✗ リポジトリ作成失敗: {response.status_code}")
            print(f"  エラー: {response.json().get('message', 'Unknown error')}")
            return None
            
    def setup_local_repo(self, repo_data, local_path="."):
        """ローカルリポジトリをセットアップ"""
        if not repo_data:
            return False
            
        commands = [
            f"git remote add origin {repo_data['clone_url']}",
            "git branch -M main",
            "git push -u origin main"
        ]
        
        print("\n以下のコマンドを実行してください:")
        for cmd in commands:
            print(f"  {cmd}")
            
        return True


def main():
    creator = GitHubRepoCreator()
    
    print("=== GitHub リポジトリ作成ツール ===\n")
    
    # リポジトリ情報の入力
    repo_name = input("リポジトリ名 (proposal-system): ").strip()
    if not repo_name:
        repo_name = "proposal-system"
        
    description = input("説明 (入札提案書作成支援システム): ").strip()
    if not description:
        description = "入札提案書作成支援システム"
        
    private_input = input("プライベートリポジトリ? (y/N): ").strip().lower()
    private = private_input == 'y'
    
    # リポジトリ作成
    repo_data = creator.create_repository(repo_name, description, private)
    
    if repo_data:
        # ローカル設定
        creator.setup_local_repo(repo_data)
        
        # .envファイルにトークンを保存する選択肢
        save_token = input("\n今後のためにトークンを.envファイルに保存しますか? (y/N): ").strip().lower()
        if save_token == 'y':
            env_path = Path(".env.local")
            with open(env_path, 'w') as f:
                f.write(f"GITHUB_TOKEN={creator.token}\n")
            print(f"✓ トークンを {env_path} に保存しました")
            print("  注意: このファイルは.gitignoreに追加してください")
            
            # .gitignoreに追加
            gitignore_path = Path(".gitignore")
            if gitignore_path.exists():
                content = gitignore_path.read_text()
                if '.env.local' not in content:
                    gitignore_path.write_text(content + "\n.env.local\n")
            else:
                gitignore_path.write_text(".env.local\n")


if __name__ == "__main__":
    main()