import streamlit as st
import database as db
from datetime import datetime
import os

def show_live():
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
        .court-card {
            background-color: white; border-radius: 12px; padding: 15px;
            border: 1px solid #ddd; text-align: center; margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 세션 상태 초기화
    if 'waiting_list' not in st.session_state: st.session_state.waiting_list = []
    if 'court_status' not in st.session_state:
        st.session_state.court_status = {5: [], 6: [], 7: [], 9: []}

    # --- [사이드바: 대기열 관리] ---
    with st.sidebar:
        if os.path.exists("img/band_cover.jpg"):
            st.image("img/band_cover.jpg", use_container_width=True)
        
        st.markdown("<h3 style='color:white;'>⏳ 실시간 대기</h3>", unsafe_allow_html=True)
        
        # 대기 중인 자석 리스트
        for idx, p in enumerate(st.session_state.waiting_list):
            wait_min = int((datetime.now() - p['check_in']).total_seconds() / 60)
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"<div class='magnet rank-a'><span class='mag-text'>{p['name']}</span><span class='wait-tag'>{wait_min}분</span></div>", unsafe_allow_html=True)
            with cols[1]:
                # 코트 배정 버튼
                if st.button("배정", key=f"assign_{idx}"):
                    st.session_state.selected_player = (idx, p)
                    st.toast(f"{p['name']} 선수를 배정할 코트를 선택하세요.")

        st.divider()
        with st.expander("🙋 도착 확인 (콕 내기)", expanded=True):
            members = db.get_members()
            for m in members:
                if not any(w['id'] == m['id'] for w in st.session_state.waiting_list) and \
                   not any(m['id'] in [u['id'] for u in players] for players in st.session_state.court_status.values()):
                    if st.button(f"🏸 {m['name']}", key=f"btn_{m['id']}", use_container_width=True):
                        m['check_in'] = datetime.now()
                        st.session_state.waiting_list.append(m)
                        st.rerun()

    # --- [메인: 라이브 코트 상황판] ---
    st.title("🏟️ 라이브 상황실")
    
    c_cols = st.columns(4)
    courts = [5, 6, 7, 9]

    for i, c_num in enumerate(courts):
        with c_cols[i]:
            st.markdown(f"<div class='court-card'>", unsafe_allow_html=True)
            st.subheader(f"{c_num}번 코트")
            
            current_players = st.session_state.court_status[c_num]
            
            # 코트 내 자리 (4자리) 표시
            for slot in range(4):
                if slot < len(current_players):
                    p = current_players[slot]
                    st.markdown(f"<div class='magnet rank-b'>{p['name']}</div>", unsafe_allow_html=True)
                else:
                    if st.button(f"빈자리 {slot+1}", key=f"slot_{c_num}_{slot}"):
                        if 'selected_player' in st.session_state:
                            idx, p_data = st.session_state.selected_player
                            st.session_state.court_status[c_num].append(p_data)
                            st.session_state.waiting_list.pop(idx) # 대기열에서 삭제
                            del st.session_state.selected_player
                            st.rerun()
            
            if len(current_players) > 0:
                if st.button("경기 종료", key=f"end_{c_num}"):
                    st.session_state.court_status[c_num] = []
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    show_live()