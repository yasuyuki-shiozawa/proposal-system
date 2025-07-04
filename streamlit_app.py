import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64

# ページ設定
st.set_page_config(
    page_title="入札提案書作成支援システム",
    page_icon="📄",
    layout="wide"
)

# セッション状態の初期化
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# タイトル
st.title("📄 入札提案書作成支援システム")
st.markdown("---")

# サイドバー
with st.sidebar:
    st.header("🔧 メニュー")
    page = st.radio(
        "機能を選択",
        ["🏠 ホーム", "📋 新規案件登録", "🔍 仕様書分析", "✍️ 提案書生成", "📚 過去案件"]
    )

# メイン画面
if page == "🏠 ホーム":
    st.header("ようこそ！")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**📋 新規案件登録**\n\n仕様書PDFをアップロードして新しい案件を登録")
    
    with col2:
        st.success("**🔍 仕様書分析**\n\n要件や評価基準を自動抽出")
    
    with col3:
        st.warning("**✍️ 提案書生成**\n\nテンプレートから提案書を自動生成")
    
    st.markdown("### 📊 統計情報")
    st.metric("登録案件数", len(st.session_state.projects))

elif page == "📋 新規案件登録":
    st.header("新規案件登録")
    
    with st.form("new_project"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("案件名 *")
            client_name = st.text_input("発注者名 *")
            deadline = st.date_input("提出期限")
        
        with col2:
            budget = st.number_input("予算上限（円）", min_value=0)
            category = st.selectbox("業務分類", 
                ["市民意識調査", "満足度調査", "ニーズ調査", "その他"])
        
        uploaded_file = st.file_uploader("仕様書PDF", type=['pdf'])
        
        notes = st.text_area("備考")
        
        submitted = st.form_submit_button("登録")
        
        if submitted and project_name and client_name:
            project = {
                'id': len(st.session_state.projects) + 1,
                'name': project_name,
                'client': client_name,
                'deadline': deadline.strftime('%Y-%m-%d'),
                'budget': budget,
                'category': category,
                'notes': notes,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if uploaded_file:
                # PDFの内容を擬似的に読み取り（実際にはpdfplumberなどを使用）
                project['pdf_content'] = f"[{uploaded_file.name}の内容がここに表示されます]"
            
            st.session_state.projects.append(project)
            st.success(f"✅ 案件「{project_name}」を登録しました！")
            st.balloons()

elif page == "🔍 仕様書分析":
    st.header("仕様書分析")
    
    if st.session_state.projects:
        selected_project = st.selectbox(
            "分析する案件を選択",
            [f"{p['name']} ({p['client']})" for p in st.session_state.projects]
        )
        
        if st.button("分析開始"):
            with st.spinner("分析中..."):
                # 分析の擬似実行
                import time
                time.sleep(2)
                
                st.session_state.current_analysis = {
                    'requirements': [
                        "調査対象: 市内在住の20歳以上の市民",
                        "サンプル数: 1,000名以上",
                        "調査方法: インターネット調査",
                        "調査期間: 契約後2ヶ月以内",
                        "成果物: 調査報告書、集計データ、プレゼン資料"
                    ],
                    'evaluation_criteria': {
                        '業務理解度': 20,
                        '実施方針・手法': 30,
                        '実施体制': 20,
                        '工程計画': 10,
                        '類似業務実績': 10,
                        '独自提案': 10
                    },
                    'keywords': ["市民意識", "満足度", "インターネット調査", "統計分析", "報告書作成"]
                }
            
            st.success("✅ 分析完了！")
    
    if st.session_state.current_analysis:
        st.subheader("📋 抽出された要件")
        for req in st.session_state.current_analysis['requirements']:
            st.write(f"• {req}")
        
        st.subheader("📊 評価基準")
        df = pd.DataFrame(
            list(st.session_state.current_analysis['evaluation_criteria'].items()),
            columns=['評価項目', '配点']
        )
        st.dataframe(df)
        
        st.subheader("🔑 キーワード")
        st.write(", ".join(st.session_state.current_analysis['keywords']))
    else:
        st.info("まず案件を登録し、分析を実行してください。")

elif page == "✍️ 提案書生成":
    st.header("提案書生成")
    
    if st.session_state.projects:
        selected_project = st.selectbox(
            "提案書を生成する案件",
            [f"{p['name']} ({p['client']})" for p in st.session_state.projects]
        )
        
        template = st.selectbox(
            "テンプレート選択",
            ["標準テンプレート", "詳細版テンプレート", "簡易版テンプレート"]
        )
        
        if st.button("生成開始"):
            with st.spinner("提案書を生成中..."):
                import time
                time.sleep(3)
                
                # 擬似的な提案書内容
                proposal_content = f"""
# {selected_project.split('(')[0].strip()} 提案書

## 1. 提案概要
弊社は、本調査業務において、豊富な実績と専門性を活かし、
質の高い調査結果をご提供いたします。

## 2. 業務理解
本業務の目的を十分に理解し、求められる成果を確実に達成いたします。

## 3. 実施方針
- 科学的な調査設計
- 適切なサンプリング
- 厳格な品質管理

## 4. 実施体制
- プロジェクトマネージャー: 1名
- 調査員: 3名
- 分析担当: 2名

## 5. スケジュール
契約後2ヶ月以内に全ての成果物を納品いたします。

[以下、詳細な内容が続きます...]
"""
                
            st.success("✅ 提案書を生成しました！")
            
            # ダウンロードボタン
            st.download_button(
                label="📥 提案書をダウンロード",
                data=proposal_content,
                file_name=f"提案書_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
            # プレビュー
            with st.expander("提案書プレビュー"):
                st.markdown(proposal_content)
    else:
        st.info("まず案件を登録してください。")

elif page == "📚 過去案件":
    st.header("過去案件一覧")
    
    if st.session_state.projects:
        df = pd.DataFrame(st.session_state.projects)
        
        # フィルター
        col1, col2 = st.columns(2)
        with col1:
            filter_client = st.selectbox("発注者でフィルター", 
                ["全て"] + list(df['client'].unique()))
        with col2:
            filter_category = st.selectbox("業務分類でフィルター",
                ["全て"] + list(df['category'].unique()))
        
        # フィルター適用
        if filter_client != "全て":
            df = df[df['client'] == filter_client]
        if filter_category != "全て":
            df = df[df['category'] == filter_category]
        
        # 表示
        st.dataframe(
            df[['name', 'client', 'deadline', 'budget', 'category', 'created_at']],
            use_container_width=True
        )
        
        # 詳細表示
        if st.checkbox("詳細を表示"):
            selected_id = st.selectbox("案件を選択", df['id'].tolist())
            selected = df[df['id'] == selected_id].iloc[0]
            
            st.subheader(f"📋 {selected['name']}")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**発注者:** {selected['client']}")
                st.write(f"**期限:** {selected['deadline']}")
                st.write(f"**予算:** ¥{selected['budget']:,}")
            with col2:
                st.write(f"**分類:** {selected['category']}")
                st.write(f"**登録日:** {selected['created_at']}")
            
            if selected.get('notes'):
                st.write(f"**備考:** {selected['notes']}")
    else:
        st.info("登録された案件はまだありません。")

# フッター
st.markdown("---")
st.markdown("🏢 入札提案書作成支援システム v1.0")