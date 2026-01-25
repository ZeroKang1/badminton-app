import streamlit as st
import database as db

def show_admin():
    st.title("📅 모임 관리 시스템")
    
    # 1. 모임 생성 (ID 101부터 시작)
    with st.expander("➕ 새 모임 등록", expanded=False):
        with st.form("session_form"):
            d = st.date_input("날짜")
            p = st.text_input("장소", "영등포다목적체육관")
            c = st.number_input("코트 수", 1, 10, 4)
            if st.form_submit_button("등록"):
                db.create_session({"date": str(d), "place": p, "courts_count": c})
                st.success("등록 완료!")
                st.rerun()

    # 2. 회원 관리 및 접수 (생략 가능)
    st.subheader("👥 회원 명단")
    members = db.get_members()
    st.dataframe(members)

if __name__ == "__main__":
    show_admin()