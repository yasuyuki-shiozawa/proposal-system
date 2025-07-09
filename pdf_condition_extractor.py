import streamlit as st
import pdfplumber
import re
import pandas as pd
from io import StringIO

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

# メインエリア
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 PDFアップロード")
    uploaded_file = st.file_uploader(
        "入札説明書をアップロード",
        type=['pdf'],
        help="入札説明書、仕様書などのPDFファイル"
    )

# 参加条件を抽出する関数
def extract_conditions(text):
    """テキストから参加条件を抽出"""
    conditions = []
    
    # 参加条件のキーワードパターン
    patterns = [
        # 資格関連
        r'.*(?:資格|免許|許可|認定|登録).*(?:を有する|している|保有|取得)',
        # 実績関連
        r'.*(?:実績|経験|履行|完了).*(?:があること|を有する|以上)',
        # 財務関連
        r'.*(?:資本金|売上高|純資産).*(?:以上|を超える)',
        # 人員関連
        r'.*(?:技術者|従業員|職員|スタッフ).*(?:配置|常駐|以上)',
        # 地域要件
        r'.*(?:本店|支店|営業所|事業所).*(?:を有する|設置|所在)',
        # ISO等
        r'.*(?:ISO|JIS|認証).*(?:取得|認定)',
        # その他の条件
        r'.*(?:であること|とする|必要がある|条件とする).*'
    ]
    
    lines = text.split('\n')
    
    # 参加資格のセクションを探す
    in_condition_section = False
    section_keywords = ['参加資格', '入札参加資格', '応募資格', '資格要件', '参加条件']
    
    for i, line in enumerate(lines):
        # セクションの開始を検出
        if any(keyword in line for keyword in section_keywords):
            in_condition_section = True
            continue
            
        # セクションの終了を検出
        if in_condition_section and re.match(r'^\d+[\.\s]|^第\d+|^（\d+）', line):
            if not any(keyword in line for keyword in ['資格', '条件', '要件']):
                in_condition_section = False
        
        # 条件の抽出
        if in_condition_section or any(re.match(pattern, line.strip()) for pattern in patterns):
            line_clean = line.strip()
            if len(line_clean) > 10 and len(line_clean) < 200:  # 適切な長さ
                # 条件番号を付与
                if re.match(r'^[（\(]\d+[）\)]', line_clean):
                    conditions.append(line_clean)
                elif re.match(r'^\d+[\.\s]', line_clean):
                    conditions.append(line_clean)
                elif line_clean and not line_clean.endswith('。'):
                    # 番号がない場合は追加
                    conditions.append(f"・ {line_clean}")
    
    return conditions

# PDFが アップロードされた場合
if uploaded_file is not None:
    with st.spinner('PDFを処理中...'):
        try:
            # PDFからテキストを抽出
            pdf_text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pdf_text += page_text + "\n"
            
            # 結果表示
            with col2:
                st.subheader("📝 抽出されたテキスト")
                
                # テキスト表示（スクロール可能）
                text_container = st.container()
                with text_container:
                    st.text_area(
                        "PDFテキスト",
                        pdf_text[:3000] + "..." if len(pdf_text) > 3000 else pdf_text,
                        height=400,
                        help="最初の3000文字を表示"
                    )
            
            # 参加条件の抽出
            st.markdown("---")
            st.subheader("🔍 抽出された参加条件")
            
            conditions = extract_conditions(pdf_text)
            
            if conditions:
                # 条件を表示
                condition_df = pd.DataFrame(conditions, columns=['参加条件'])
                condition_df.index = condition_df.index + 1
                condition_df.index.name = 'No.'
                
                st.dataframe(condition_df, use_container_width=True)
                
                # ダウンロードボタン
                col1_dl, col2_dl, col3_dl = st.columns(3)
                
                with col1_dl:
                    # CSV形式
                    csv = condition_df.to_csv(index=True, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 CSVダウンロード",
                        data=csv,
                        file_name=f"参加条件_{uploaded_file.name.replace('.pdf', '')}.csv",
                        mime="text/csv"
                    )
                
                with col2_dl:
                    # テキスト形式
                    text_output = "\n".join([f"{i+1}. {cond}" for i, cond in enumerate(conditions)])
                    st.download_button(
                        label="📥 テキストダウンロード",
                        data=text_output,
                        file_name=f"参加条件_{uploaded_file.name.replace('.pdf', '')}.txt",
                        mime="text/plain"
                    )
                
                with col3_dl:
                    # 全テキスト
                    st.download_button(
                        label="📥 PDF全文ダウンロード",
                        data=pdf_text,
                        file_name=f"全文_{uploaded_file.name.replace('.pdf', '')}.txt",
                        mime="text/plain"
                    )
                
                # 統計情報
                st.info(f"✅ {len(conditions)}個の参加条件を抽出しました")
                
            else:
                st.warning("参加条件が見つかりませんでした。別のPDFをお試しください。")
                
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.info("PDFが正しく読み込めない場合は、別のPDFをお試しください。")

else:
    # 使用例
    st.markdown("### 💡 使用例")
    st.markdown("""
    このシステムは以下のような参加条件を自動抽出します：
    
    - **資格要件**: 「建設業の許可を有すること」
    - **実績要件**: 「過去5年間に同種業務の実績があること」
    - **財務要件**: 「資本金1000万円以上」
    - **人員要件**: 「主任技術者を配置できること」
    - **地域要件**: 「○○市内に本店を有すること」
    """)
    
    st.info("👆 入札説明書のPDFをアップロードしてください")