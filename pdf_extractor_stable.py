import streamlit as st
import pdfplumber
import pandas as pd
import io

st.set_page_config(
    page_title="入札参加条件抽出システム",
    page_icon="📄",
    layout="wide"
)

st.title("📄 入札参加条件抽出システム")
st.markdown("入札説明書のPDFから参加条件を自動抽出します")

# サイドバー
with st.sidebar:
    st.header("📋 機能説明")
    st.info(
        "1. PDFをアップロード\n"
        "2. テキストを自動抽出\n"
        "3. 表形式データも抽出\n"
        "4. 参加条件を検出"
    )
    
    # 設定オプション
    st.subheader("⚙️ 抽出設定")
    extract_tables = st.checkbox("表を抽出", value=True)
    debug_mode = st.checkbox("デバッグモード", value=True)

# メインエリア
uploaded_file = st.file_uploader(
    "入札説明書をアップロード",
    type=['pdf'],
    help="入札説明書、仕様書などのPDFファイル"
)

# 表データを整形する関数
def format_table(table):
    """表データを読みやすく整形"""
    if not table:
        return ""
    
    formatted_rows = []
    for row in table:
        # None値を空文字に変換
        cleaned_row = [str(cell).strip() if cell else "" for cell in row]
        # 空行をスキップ
        if any(cleaned_row):
            formatted_rows.append(" | ".join(cleaned_row))
    
    return "\n".join(formatted_rows)

# PDFからテキストと表を抽出する関数
def extract_all_content(pdf_file):
    """PDFから全コンテンツ（テキスト＋表）を抽出"""
    all_text = []
    page_contents = []
    all_tables = []
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            st.write(f"📄 総ページ数: {len(pdf.pages)}")
            
            # プログレスバー
            progress_bar = st.progress(0)
            
            for i, page in enumerate(pdf.pages):
                page_data = {
                    'page': i + 1,
                    'text': "",
                    'tables': [],
                    'char_count': 0,
                    'table_count': 0
                }
                
                try:
                    # テキスト抽出
                    page_text = page.extract_text()
                    
                    # 表の抽出（extract_tablesオプションが有効な場合）
                    tables = []
                    if extract_tables:
                        try:
                            # シンプルな設定で表を抽出
                            extracted_tables = page.extract_tables()
                            if extracted_tables:
                                tables = extracted_tables
                                page_data['table_count'] = len(tables)
                                
                                # 表をテキストに変換
                                table_texts = []
                                for j, table in enumerate(tables):
                                    if table and len(table) > 0:  # 空の表をチェック
                                        table_text = f"\n[表{j+1}]\n"
                                        table_text += format_table(table)
                                        table_texts.append(table_text)
                                        
                                        # DataFrameとしても保存
                                        try:
                                            # 表が有効かチェック
                                            if len(table) > 1 and len(table[0]) > 0:
                                                # ヘッダーありの場合
                                                df = pd.DataFrame(table[1:], columns=table[0])
                                            else:
                                                # ヘッダーなしの場合
                                                df = pd.DataFrame(table)
                                            
                                            page_data['tables'].append({
                                                'index': j + 1,
                                                'dataframe': df,
                                                'text': table_text
                                            })
                                            
                                            all_tables.append({
                                                'page': i + 1,
                                                'table_index': j + 1,
                                                'dataframe': df
                                            })
                                        except Exception as e:
                                            if debug_mode:
                                                st.warning(f"表{j+1}のDataFrame変換エラー: {str(e)}")
                        except Exception as e:
                            if debug_mode:
                                st.warning(f"ページ{i+1}の表抽出エラー: {str(e)}")
                    
                    # ページコンテンツの結合
                    if page_text:
                        all_text.append(f"\n--- ページ {i+1} ---\n")
                        all_text.append(page_text)
                        page_data['text'] = page_text
                        page_data['char_count'] = len(page_text)
                        
                        # 表がある場合は追加
                        if 'table_texts' in locals() and table_texts:
                            for table_text in table_texts:
                                all_text.append(table_text)
                                page_data['char_count'] += len(table_text)
                    elif tables:
                        # テキストはないが表がある場合
                        all_text.append(f"\n--- ページ {i+1} (表のみ) ---\n")
                        if 'table_texts' in locals() and table_texts:
                            for table_text in table_texts:
                                all_text.append(table_text)
                                page_data['char_count'] += len(table_text)
                    else:
                        all_text.append(f"\n--- ページ {i+1} (コンテンツなし) ---\n")
                    
                    page_contents.append(page_data)
                    
                    # プログレスバー更新
                    progress_bar.progress((i + 1) / len(pdf.pages))
                    
                except Exception as e:
                    st.warning(f"ページ {i+1} の処理中にエラー: {str(e)}")
                    page_contents.append({
                        'page': i + 1,
                        'text': f"エラー: {str(e)}",
                        'tables': [],
                        'char_count': 0,
                        'table_count': 0
                    })
            
            progress_bar.empty()
            
    except Exception as e:
        st.error(f"PDF読み込みエラー: {str(e)}")
        return "", [], []
    
    return "\n".join(all_text), page_contents, all_tables

# PDFがアップロードされた場合
if uploaded_file is not None:
    st.subheader("📊 PDF解析結果")
    
    # コンテンツ抽出
    with st.spinner('PDFを解析中...'):
        full_text, page_info, all_tables = extract_all_content(uploaded_file)
    
    # 抽出統計
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("総文字数", f"{len(full_text):,}")
    with col2:
        st.metric("総ページ数", len(page_info))
    with col3:
        total_tables = sum(p['table_count'] for p in page_info)
        st.metric("検出された表", total_tables)
    with col4:
        avg_chars = sum(p['char_count'] for p in page_info) / len(page_info) if page_info else 0
        st.metric("平均文字数/ページ", f"{avg_chars:,.0f}")
    
    # タブで表示
    tabs = st.tabs(["📝 全文表示", "📊 ページ別分析", "📋 表一覧", "🔍 参加条件抽出"])
    
    with tabs[0]:
        st.subheader("抽出されたテキスト（全文）")
        
        # 表示オプション
        show_all = st.checkbox("全文を表示", value=False)
        
        if show_all:
            st.text_area(
                "PDF全文（テキスト＋表）",
                full_text,
                height=600,
                help="Ctrl+Fで検索できます"
            )
        else:
            display_text = full_text[:5000] + "..." if len(full_text) > 5000 else full_text
            st.text_area(
                "PDF全文（最初の5000文字）",
                display_text,
                height=400
            )
        
        # ダウンロードボタン
        st.download_button(
            label="📥 全文をダウンロード",
            data=full_text,
            file_name=f"全文_{uploaded_file.name.replace('.pdf', '')}.txt",
            mime="text/plain"
        )
    
    with tabs[1]:
        st.subheader("ページ別コンテンツ分析")
        
        # ページ情報をDataFrameに変換
        try:
            df_summary = pd.DataFrame([{
                'ページ': p['page'],
                '文字数': p['char_count'],
                '表の数': p['table_count']
            } for p in page_info])
            
            # グラフ表示
            col1, col2 = st.columns(2)
            with col1:
                st.write("### 文字数分布")
                if not df_summary.empty:
                    st.bar_chart(df_summary.set_index('ページ')['文字数'])
            
            with col2:
                st.write("### 表の分布")
                if not df_summary.empty:
                    st.bar_chart(df_summary.set_index('ページ')['表の数'])
            
            # 詳細表示
            if debug_mode:
                st.write("### 詳細情報")
                st.dataframe(df_summary, use_container_width=True)
                
                # 問題のあるページを特定
                if not df_summary.empty:
                    problem_pages = df_summary[df_summary['文字数'] < 100]
                    if not problem_pages.empty:
                        st.warning(f"⚠️ コンテンツが少ないページ: {problem_pages['ページ'].tolist()}")
        except Exception as e:
            st.error(f"ページ分析エラー: {str(e)}")
    
    with tabs[2]:
        st.subheader("検出された表一覧")
        
        if all_tables:
            for idx, table_info in enumerate(all_tables):
                try:
                    with st.expander(f"📋 ページ {table_info['page']} - 表 {table_info['table_index']}"):
                        st.dataframe(table_info['dataframe'], use_container_width=True)
                        
                        # CSV形式でダウンロード
                        csv = table_info['dataframe'].to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📥 この表をCSVでダウンロード",
                            data=csv,
                            file_name=f"表_P{table_info['page']}_T{table_info['table_index']}.csv",
                            mime="text/csv",
                            key=f"table_{idx}"  # ユニークなキーを使用
                        )
                except Exception as e:
                    st.error(f"表の表示エラー: {str(e)}")
        else:
            st.info("表形式のデータは検出されませんでした")
    
    with tabs[3]:
        st.subheader("参加条件の抽出")
        
        # 参加条件のキーワード検索
        keywords = ["参加資格", "入札参加資格", "応募資格", "資格要件", "参加条件", "入札参加要件"]
        
        found_sections = []
        lines = full_text.split('\n')
        
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword in line:
                    start = max(0, i - 3)
                    end = min(len(lines), i + 15)
                    context = '\n'.join(lines[start:end])
                    found_sections.append({
                        'keyword': keyword,
                        'line_number': i + 1,
                        'context': context
                    })
        
        if found_sections:
            st.success(f"✅ {len(found_sections)}箇所で参加条件関連のキーワードを発見")
            
            # 重複を除去
            unique_sections = []
            seen_contexts = set()
            
            for section in found_sections:
                context_key = section['context'][:100]  # 最初の100文字で重複判定
                if context_key not in seen_contexts:
                    unique_sections.append(section)
                    seen_contexts.add(context_key)
            
            for i, section in enumerate(unique_sections[:10]):  # 最大10件表示
                with st.expander(f"📍 {section['keyword']} (行 {section['line_number']})"):
                    st.text(section['context'])
        else:
            st.warning("参加条件に関するキーワードが見つかりませんでした")

else:
    # 使用方法の説明
    st.info("👆 入札説明書のPDFをアップロードしてください")
    
    st.markdown("""
    ### 🔧 機能の特徴
    
    1. **安定したPDF処理**
       - エラーハンドリングを強化
       - 問題があってもアプリが停止しない
       - デバッグ情報の表示
    
    2. **表の抽出**
       - 基本的な表構造を認識
       - CSV形式でダウンロード可能
       - 表ごとに個別管理
    
    3. **参加条件の検索**
       - キーワードベースの検索
       - 前後の文脈を含めて表示
       - 重複を自動除去
    """)