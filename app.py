import streamlit as st
from admin_page import show_admin
from live_board import show_live

st.sidebar.title("🏸 메뉴")
page = st.sidebar.radio("이동할 페이지", ["상황실 (Live)", "모임 관리 (Admin)"])

if page == "상황실 (Live)":
    show_live()
else:
    show_admin()

# streamlit run app.py