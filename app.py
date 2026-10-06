import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Racing Attack Game",
    page_icon="🏎",
    layout="centered"
)

st.title("🏎️ Racing Attack")
st.caption("Game đua xe Racing Attack phong cách Retro!")

# HTML/CSS/JS code
game_code = r"""








HTML
<canvas id="gameCanvas" width="360" height="480"></canvas>
◄ Trái (A)

Bắt đầu / OK

Phải (D) ►

Điều khiển: Phím ◄ / ► hoặc A / D | Enter / Space để chơi lại

"""

components.html(game_code, height=620)
