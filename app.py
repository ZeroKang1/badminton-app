import streamlit as st
from admin_page import show_admin
from live_board import show_live

# ============================================================
# 설정
# ============================================================
APP_NAME = "소꾹"  # 배드민턴 소모임 위꾹
APP_VERSION = "2.1.0"

# 페이지 설정
st.set_page_config(
    page_title=f"🏸 {APP_NAME}",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 사이드바 메뉴
st.sidebar.markdown(f"""
<div style="text-align:center; padding:15px 0;">
    <span style="font-size:36px;">🏸</span>
    <h2 style="margin:8px 0;">{APP_NAME}</h2>
    <p style="color:#666; font-size:11px;">배드민턴 소모임 위꾹</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "메뉴",
    ["📺 라이브", "⚙️ 운영관리"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# 하단 정보
st.sidebar.markdown(f"""
<div style="position:fixed; bottom:15px; left:15px; font-size:10px; color:#999;">
    <p>v{APP_VERSION}</p>
    <p>© 2024 {APP_NAME}</p>
</div>
""", unsafe_allow_html=True)

# 페이지 라우팅
if page == "📺 라이브":
    show_live()
else:
    show_admin()
