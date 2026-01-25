import streamlit as st
import pandas as pd
from datetime import datetime
import database as db
import time

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="여민소 민턴 전광판")

# 2. 스타일 (기존 스타일 유지 및 대기시간 텍스트 추가)
st.markdown("""
    <style>
    section[data-testid="stSidebar"] { width: 350px !important; background-color: #245c4b; }
    .stApp { background-color: #f8f9fa; } 
    .magnet {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        width: 92%; height: 50px; border-radius: 6px; margin: 4px auto;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.2); border: 1.5px solid #fff; background-color: white;
    }
    .mag-text { font-size: 15px; font-weight: 700; color: #222; }
    .wait-time { font-size: 10px; color: #d81b60; font-weight: bold; margin-top: -2px; }

    /* 급수별 색상 */
    .rank-s { background-color: #ffcdd2; border-color: #e57373; }
    .rank-a { background-color: #ffe0b2; border-color: #ffb74d; }
    .rank-b { background-color: #fff9c4; border-color: #fff176; }
    .rank-c { background-color: #c8e6c9; border-color: #81c784; }
    .rank-d { background-color: #bbdefb; border-color: #64b5f6; }
    .rank-begin { background-color: #e1bee7; border-color: #ba68c8; }
    </style>
    """, unsafe_allow_html=True)

# --- [좌측 사이드바: 자석 관리] ---
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🌸 여민소 & 민턴</h2>", unsafe_allow_html=True)
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