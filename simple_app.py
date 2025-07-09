import streamlit as st

st.title("入札提案書作成支援システム")
st.write("シンプルバージョン - テスト中")

# 基本的な入力
with st.form("basic_form"):
    project_name = st.text_input("案件名")
    client_name = st.text_input("発注者名")
    submitted = st.form_submit_button("登録")
    
    if submitted and project_name:
        st.success(f"案件「{project_name}」を登録しました！")
        
st.info("このアプリは開発中です。機能は順次追加されます。")