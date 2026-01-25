# 2. admin_page.py (모임 등록 및 접수 관리)
# 모임 날짜를 정하고 누가 올지 미리 체크하는 화면입니다.

import streamlit as st
import database as db

st.title("📅 모임 관리 및 접수")

# 1. 새 모임 등록
with st.expander("➕ 새 모임 만들기", expanded=False):
    with st.form("new_session"):
        date = st.date_input("날짜")
        place = st.text_input("장소", value="민턴캐슬")
        courts = st.number_input("코트 수", min_value=1, value=4)
        if st.form_submit_button("모임 생성"):
            db.create_session({"date": str(date), "place": place, "courts_count": courts})
            st.success("새 모임이 등록되었습니다! (ID: 101~)")
            st.rerun()

# 2. 모임 선택 및 참가자 접수
sessions = db.get_sessions()
if sessions:
    session_options = {f"[{s['id']}] {s['date']} {s['place']}": s['id'] for s in sessions}
    sel_session_name = st.selectbox("관리할 모임 선택", options=session_options.keys())
    sel_session_id = session_options[sel_session_name]

    st.subheader("🙋 참가 신청 접수")
    all_m = db.get_members()
    # 여기에 체크박스 형태로 참석 인원을 선택하고 'attendance' 테이블에 저장하는 로직 추가