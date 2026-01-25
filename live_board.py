# 3. live_board.py (라이브 상황실)
# 실제 현장에서 콕을 내고 대기 시간을 보며 대진을 짜는 화면입니다.

import streamlit as st
import database as db
from datetime import datetime
import os

st.set_page_config(layout="wide")

# 스타일 설정
st.markdown("""
    <style>
    section[data-testid="stSidebar"] { width: 350px !important; background-color: #245c4b; padding-top: 10px !important; }
    .magnet {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        width: 92%; height: 50px; border-radius: 6px; margin: 4px auto;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.2); border: 1.5px solid #fff; background-color: white;
    }
    .mag-text { font-size: 14px; font-weight: 700; color: #222; }
    .wait-time { font-size: 10px; color: #d81b60; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'waiting_list' not in st.session_state: st.session_state.waiting_list = []

with st.sidebar:
    # 밴드 커버 (50% 크기)
    if os.path.exists("img/band_cover.jpg"):
        st.image("img/band_cover.jpg", use_container_width=True)
    
    st.markdown("### ⏳ 실시간 대기 현황 (콕 낸 순서)")
    # 대기 명단 출력 로직
    for p in st.session_state.waiting_list:
        wait_min = int((datetime.now() - p['check_in']).total_seconds() / 60)
        st.markdown(f"<div class='magnet'><div class='mag-text'>{p['name']}</div><div class='wait-time'>{wait_min}분 대기</div></div>", unsafe_allow_html=True)

    st.write("---")
    with st.expander("📝 사전 접수자 (도착 확인)", expanded=True):
        # 임시 데이터 (나중에 DB와 연동)
        pre_list = [{"id": 1, "name": "홍길동", "rank": "A"}, {"id": 2, "name": "김철수", "rank": "B"}]
        for m in pre_list:
            if st.button(f"🏸 {m['name']} 도착", key=f"in_{m['id']}", use_container_width=True):
                m['check_in'] = datetime.now()
                st.session_state.waiting_list.append(m)
                st.rerun()

st.title("🏟️ 라이브 상황실")
# 코트 현황 및 수기 대진 로직...

import streamlit as st
import database as db
from datetime import datetime
import os

def show_live():
    # 스타일 설정 (사이드바 폭 및 자석 디자인)
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { width: 350px !important; background-color: #245c4b; padding-top: 10px !important; }
        .stApp { background-color: #f8f9fa; }
        .magnet {
            display: flex; align-items: center; justify-content: center;
            width: 90%; height: 45px; border-radius: 6px; margin: 5px auto;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1); border: 1.5px solid #fff;
        }
        .mag-text { font-size: 14px; font-weight: 700; color: #222; }
        .wait-tag { font-size: 10px; color: #d81b60; margin-left: 5px; }
        </style>
    """, unsafe_allow_html=True)

    # 세션 상태 초기화
    if 'waiting_list' not in st.session_state: st.session_state.waiting_list = []

    # --- [사이드바: 현장 도착 확인] ---
    with st.sidebar:
        if os.path.exists("img/band_cover.jpg"):
            st.image("img/band_cover.jpg", use_container_width=True)
        
        st.markdown("<h3 style='color:white;'>⏳ 대기 중 (콕 낸 순서)</h3>", unsafe_allow_html=True)
        # 대기 자석 표시
        for p in st.session_state.waiting_list:
            wait_min = int((datetime.now() - p['check_in']).total_seconds() / 60)
            st.markdown(f"<div class='magnet rank-a'><span class='mag-text'>{p['name']}</span><span class='wait-tag'>{wait_min}분</span></div>", unsafe_allow_html=True)

        st.divider()
        with st.expander("🙋 사전 접수자 (도착 확인)", expanded=True):
            # 임시 데이터 (DB 연동 시 db.get_members() 사용)
            members = db.get_members()
            for m in members:
                if not any(w['id'] == m['id'] for w in st.session_state.waiting_list):
                    label = f"🏸 {m['name']}{str(m.get('birth',''))[-2:]}{m.get('rank','')}"
                    if st.button(label, key=f"btn_{m['id']}", use_container_width=True):
                        m['check_in'] = datetime.now()
                        st.session_state.waiting_list.append(m)
                        st.rerun()

    # --- [메인: 코트 현황] ---
    st.title("🏟️ 라이브 상황실")
    # 여기에 코트 5, 6, 7, 9번 그리드 배치 및 수기 매칭 로직 추가

if __name__ == "__main__":
    show_live()