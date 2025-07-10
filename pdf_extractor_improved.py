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
        "3. 参加条件を自動検出\n"
        "4. 結果をダウンロード"
    )
    
    # デバッグモード
    debug_mode = st.checkbox("デバッグモード", value=True)

# メインエリア
uploaded_file = st.file_uploader(
    "入札説明書をアップロード",
    type=['pdf'],
    help="入札説明書、仕様書などのPDFファイル"
)

# PDFからテキストを抽出する改善版関数
def extract_text_from_pdf(pdf_file):
    """PDFから全テキストを確実に抽出"""
    all_text = []
    page_texts = []
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            st.write(f"📄 総ページ数: {len(pdf.pages)}")
            
            # プログレスバー
            progress_bar = st.progress(0)
            
            for i, page in enumerate(pdf.pages):
                try:
                    # ページごとのテキスト抽出
                    page_text = page.extract_text()
                    
                    if page_text:
                        all_text.append(f"\n--- ページ {i+1} ---\n")
                        all_text.append(page_text)
                        page_texts.append({
                            'page': i+1,
                            'text': page_text,
                            'char_count': len(page_text)
                        })
                    else:
                        # テキストが抽出できない場合の代替手段
                        # テーブルとして抽出を試みる
                        tables = page.extract_tables()
                        if tables:
                            table_text = "\n".join([
                                "\n".join([str(cell) if cell else "" for cell in row])
                                for table in tables for row in table
                            ])
                            all_text.append(f"\n--- ページ {i+1} (表形式) ---\n")
                            all_text.append(table_text)
                            page_texts.append({
                                'page': i+1,
                                'text': table_text,
                                'char_count': len(table_text)
                            })
                        else:
                            all_text.append(f"\n--- ページ {i+1} (テキストなし) ---\n")
                            page_texts.append({
                                'page': i+1,
                                'text': "（テキストを抽出できませんでした）",
                                'char_count': 0
                            })
                    
                    # プログレスバー更新
                    progress_bar.progress((i + 1) / len(pdf.pages))
                    
                except Exception as e:
                    st.warning(f"ページ {i+1} の処理中にエラー: {str(e)}")
                    page_texts.append({
                        'page': i+1,
                        'text': f"エラー: {str(e)}",
                        'char_count': 0
                    })
            
            progress_bar.empty()
            
    except Exception as e:
        st.error(f"PDF読み込みエラー: {str(e)}")
        return "", []
    
    return "\n".join(all_text), page_texts

# PDFがアップロードされた場合
if uploaded_file is not None:
    st.subheader("📊 PDF解析結果")
    
    # テキスト抽出
    with st.spinner('PDFを解析中...'):
        full_text, page_info = extract_text_from_pdf(uploaded_file)
    
    # 抽出統計
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総文字数", f"{len(full_text):,}")
    with col2:
        st.metric("総ページ数", len(page_info))
    with col3:
        avg_chars = sum(p['char_count'] for p in page_info) / len(page_info) if page_info else 0
        st.metric("平均文字数/ページ", f"{avg_chars:,.0f}")
    
    # タブで表示
    tab1, tab2, tab3 = st.tabs(["📝 全文表示", "📊 ページ別分析", "🔍 参加条件抽出"])
    
    with tab1:
        st.subheader("抽出されたテキスト（全文）")
        
        # 表示オプション
        show_all = st.checkbox("全文を表示", value=False)
        
        if show_all:
            # 全文表示
            st.text_area(
                "PDF全文",
                full_text,
                height=600,
                help="Ctrl+Fで検索できます"
            )
        else:
            # 最初の5000文字のみ表示
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
    
    with tab2:
        st.subheader("ページ別テキスト抽出状況")
        
        # ページ情報をDataFrameに変換
        df_pages = pd.DataFrame(page_info)
        
        # グラフ表示
        st.bar_chart(df_pages.set_index('page')['char_count'])
        
        # 詳細表示
        if debug_mode:
            st.dataframe(df_pages, use_container_width=True)
            
            # 問題のあるページを特定
            problem_pages = df_pages[df_pages['char_count'] < 100]
            if not problem_pages.empty:
                st.warning(f"⚠️ テキストが少ないページ: {problem_pages['page'].tolist()}")
    
    with tab3:
        st.subheader("参加条件の抽出")
        st.info("この機能は次のステップで実装します。まずはPDFテキスト抽出が正しく動作することを確認してください。")
        
        # 参加条件キーワードの検索（簡易版）
        keywords = ["参加資格", "入札参加資格", "応募資格", "資格要件", "参加条件"]
        
        found_sections = []
        lines = full_text.split('\n')
        
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword in line:
                    # 前後の文脈を含めて抽出
                    start = max(0, i - 2)
                    end = min(len(lines), i + 10)
                    context = '\n'.join(lines[start:end])
                    found_sections.append({
                        'keyword': keyword,
                        'line_number': i + 1,
                        'context': context
                    })
        
        if found_sections:
            st.success(f"✅ {len(found_sections)}箇所で参加条件関連のキーワードを発見")
            
            for section in found_sections[:5]:  # 最初の5件のみ表示
                with st.expander(f"📍 {section['keyword']} (行 {section['line_number']})"):
                    st.text(section['context'])
        else:
            st.warning("参加条件に関するキーワードが見つかりませんでした")

else:
    # 使用方法の説明
    st.info("👆 入札説明書のPDFをアップロードしてください")
    
    st.markdown("""
    ### 🔧 改善されたポイント
    
    1. **完全なテキスト抽出**
       - 全ページを確実に処理
       - ページごとの文字数を表示
       - 抽出できないページも記録
    
    2. **デバッグ機能**
       - ページ別の抽出状況を可視化
       - 問題のあるページを特定
       - 詳細なエラー情報
    
    3. **使いやすい表示**
       - タブで情報を整理
       - 全文/要約の切り替え
       - ダウンロード機能
    """)