import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Racing Attack Game",
    page_icon="🏎",
    layout="centered"
)

st.title("🏎️ Racing Attack")
st.caption("Game đua xe Racing Attack phong cách Retro!")

# Đọc file HTML từ thư mục
html_file_path = os.path.join(os.path.dirname(__file__), "index.html")

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        game_html = f.read()
    components.html(game_html, height=620)
else:
    st.error("Không tìm thấy file index.html! Hãy tạo file index.html cùng thư mục với app.py.")
