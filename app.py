import streamlit as st
import os
import pandas as pd
from datetime import datetime
import database as db
import time

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="여민소 민턴 전광판")

# 2. 스타일 (기존 스타일 유지 및 대기시간 텍스트 추가)
st.markdown("""
    <style>
    /* 사이드바 최상단 여백 줄이기 (약 3mm) */
    .st-emotion-cache-16txm9y, .st-emotion-cache-6qob1r {
        padding-top: 10px !important; /* 약 3mm 효과 */
    }

    /* 이미지 컨테이너: 중앙 정렬 및 크기 조절 */
    .sidebar-img-container {
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
    }
    .sidebar-img-container img {
        width: 90%; /* 너비 90%로 축소 */
        border-radius: 10px; /* 약간의 라운드 처리 */
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- [좌측 사이드바 구성] ---
with st.sidebar:
    # 1. 밴드 커버 이미지 (50% 크기 중앙 정렬)
    img_path = "img/band1-여민소.png"
    try:
        # 이미지를 HTML로 감싸서 크기와 정렬을 세밀하게 제어
        import base64
        def get_image_base64(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        
        if os.path.exists(img_path):
            img_base64 = get_image_base64(img_path)
            st.markdown(f"""
                <div class="sidebar-img-container">
                    <img src="data:image/jpg;base64,{img_base64}">
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown("<h2 style='text-align: center; color: white;'>🌸 여민소 & 민턴</h2>", unsafe_allow_html=True)


  # --- [사이드바 하단: 참가 접수자 목록] ---
with st.sidebar.expander("📝 사전 접수자 (도착 확인)", expanded=True):
    # status가 '접수'인 인원만 표시
    pre_registered = [p for p in st.session_state.all_members if p['status'] == '접수']
    
    for m in pre_registered:
        # 버튼에 이름생년급수 표기
        btn_label = f"{m['name']}{str(m['birth'])[-2:]}{m['rank']}"
        if st.button(f"🏸 {btn_label} 도착", key=f"arrival_{m['id']}", use_container_width=True):
            # 1. 상태를 '도착'으로 변경
            # 2. 대기 시간(check_in)을 현재 시간으로 기록
            m['check_in'] = datetime.now()
            st.session_state.waiting_list.append(m)
            # DB 업데이트 로직 (status='도착'으로 update)
            st.rerun()

    # --- [사이드바 상단: 실시간 대기 명단] ---
    st.sidebar.markdown("### ⏳ 실시간 대기 현황")
    waiting_list = st.session_state.get('waiting_list', [])

    # 대기 시간이 긴 순서로 정렬하여 표시
    sorted_waiting = sorted(waiting_list, key=lambda x: x['check_in'])

    for i in range(0, len(sorted_waiting), 3):
        cols = st.sidebar.columns(3)
        # (자석 이름표 UI 로직 적용...)

    st.divider()
    
    # 참석자 명단 및 대기시간 표시
    st.markdown("<h3 style='color: white; font-size: 18px;'>📍 대기 중인 자석</h3>", unsafe_allow_html=True)
    
    att_list = st.session_state.get('attendance', [])
    if not att_list:
        st.caption("보관함에서 자석을 꺼내주세요.")
    else:
        for i in range(0, len(att_list), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(att_list):
                    p = att_list[i+j]
                    
                    # 정보 추출
                    name = str(p.get('name', ''))
                    raw_birth = str(p.get('birth', ''))
                    birth = raw_birth[-2:] if raw_birth and raw_birth != 'None' else ''
                    rank = str(p.get('rank', 'D')).upper()
                    
                    # 대기 시간 계산
                    check_in_time = p.get('check_in', datetime.now())
                    wait_min = int((datetime.now() - check_in_time).total_seconds() / 60)
                    
                    # 급수 클래스
                    r_class = "rank-d"
                    if "S" in rank: r_class = "rank-s"
                    elif "A" in rank: r_class = "rank-a"
                    elif "B" in rank: r_class = "rank-b"
                    elif "C" in rank: r_class = "rank-c"
                    elif any(w in rank for w in ["초", "입"]): r_class = "rank-begin"

                    cols[j].markdown(f"""
                        <div class='magnet {r_class}'>
                            <div class='mag-text'>{name}{birth}{rank}</div>
                            <div class='wait-time'>{wait_min}분 대기</div>
                        </div>
                        """, unsafe_allow_html=True)

    st.write("---")
    
    # 자석 보관함 (이름+생년+급수로 표기)
    with st.expander("📥 자석 보관함"):
        all_members = db.get_members()
        for m in all_members:
            # 이미 꺼낸 자석은 제외
            if any(a['id'] == m['id'] for a in att_list):
                continue
                
            m_name = str(m.get('name', ''))
            m_birth = str(m.get('birth', ''))[-2:] if m.get('birth') else ''
            m_rank = str(m.get('rank', 'D')).upper()
            
            # 버튼 텍스트: 이름생년급수
            btn_label = f"{m_name}{m_birth}{m_rank}"
            
            if st.button(f"➕ {btn_label}", key=f"add_{m['id']}", use_container_width=True):
                if 'attendance' not in st.session_state: st.session_state.attendance = []
                # 출석 시간(체크인) 추가해서 저장
                m['check_in'] = datetime.now()
                st.session_state.attendance.append(m)
                st.rerun()

# --- [우측 메인 영역: 대진표 생성 도구] ---
st.markdown("<h2 style='color: #222;'>🎲 대진 생성 및 관리</h2>", unsafe_allow_html=True)

# 대진 생성 탭
tab1, tab2 = st.tabs(["🎮 대진 만들기", "📜 전체 경기 이력"])

with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.write("#### 1단계: 선수 선택")
        st.info("왼쪽 명단에서 대기 시간이 긴 순서대로 대진을 짜는 것이 좋습니다.")
        
        # 실제 운영 시에는 여기서 체크박스로 4명을 선택하거나 '자동 대진' 버튼을 누름
        if st.button("자동 대진표 추천 (대기순)"):
            if len(att_list) < 4:
                st.warning("선수가 4명 이상이어야 합니다.")
            else:
                # 대기 시간순 정렬 (기능 구현 예시)
                sorted_att = sorted(att_list, key=lambda x: x['check_in'])
                top4 = sorted_att[:4]
                st.session_state.suggested = top4
                st.success(f"추천 대진: {top4[0]['name']}, {top4[1]['name']} VS {top4[2]['name']}, {top4[3]['name']}")

    with c2:
        st.write("#### 2단계: 코트 배정")
        # 여기에 코트 현황 요약 및 배정 버튼 배치 예정

# 실시간 보드 (코트 상황) - 하단 배치
st.divider()
st.markdown("### 🏟️ 실시간 코트 현황")
# (이전의 코트 현황 코드와 동일하게 유지)