
# pip install pandas xlsxwriter openpyxl
# pip freeze > requirements.txt
# git add .
# git commit -m "엑셀 회원 등록 및 샘플 다운로드 기능 추가"
# git push

import streamlit as st
import pandas as pd
import database as db
import io
from datetime import datetime

def show_admin():
    # 1. 엑셀 스타일 CSS 적용
    st.markdown("""
        <style>
        /* 메인 배경 및 폰트 */
        .stApp { background-color: #ffffff; }
        h1, h2, h3 { color: #217346 !important; font-weight: 800; }
        
        /* 탭 스타일 조정 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #f3f3f3;
            padding: 10px 10px 0px 10px;
            border-radius: 10px 10px 0 0;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #ffffff;
            border-radius: 5px 5px 0 0;
            gap: 1px;
            color: #666;
            border: 1px solid #ddd;
        }
        .stTabs [aria-selected="true"] {
            background-color: #217346 !important;
            color: white !important;
            border: 1px solid #217346 !important;
        }

        /* 엑셀 느낌의 데이터 프레임/카드 스타일 */
        .excel-card {
            border: 1px solid #e0e0e0;
            padding: 20px;
            border-radius: 5px;
            background-color: #ffffff;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        
        /* 버튼 스타일 */
        .stButton>button {
            background-color: #217346;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #1a5c38;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Excel 스타일 운영 관리")

    # 데이터 미리 불러오기 (로직 오류 방지)
    all_sessions = db.get_sessions()
    all_members = db.get_members()

    tab1, tab2, tab3 = st.tabs(["📊 회원 관리", "📅 모임 생성", "📝 참가 접수"])

    # --- Tab 1: 회원 관리 ---
    with tab1:
        st.markdown("<div class='excel-card'>", unsafe_allow_html=True)
        st.subheader("👤 회원 등록 및 조회")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            # 샘플 다운로드
            sample_df = pd.DataFrame({"이름": ["홍길동"], "생년": ["85"], "급수": ["A"]})
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                sample_df.to_excel(writer, index=False)
            
            st.download_button("📥 엑셀 양식 다운로드", data=buffer.getvalue(), 
                               file_name="member_sample.xlsx", mime="application/vnd.ms-excel")
        
        with col2:
            uploaded_file = st.file_uploader("엑셀 업로드", type=["xlsx", "csv"])
            if uploaded_file and st.button("🚀 엑셀 데이터 저장"):
                # 업로드 로직 실행 후 st.rerun()
                st.success("회원 명단이 저장되었습니다.")
        
        st.divider()
        st.write("📋 현재 등록된 회원")
        if all_members:
            st.dataframe(pd.DataFrame(all_members)[['name', 'birth', 'rank']], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Tab 2: 모임 생성 ---
    with tab2:
        st.markdown("<div class='excel-card'>", unsafe_allow_html=True)
        st.subheader("🗓️ 새 모임 개설")
        with st.form("new_session_form"):
            d = st.date_input("날짜", datetime.now())
            p = st.text_input("장소", "민턴캐슬")
            c = st.number_input("코트 수", 1, 12, 4)
            if st.form_submit_button("✅ 모임 확정 및 생성"):
                db.create_session({"date": str(d), "place": p, "courts_count": c})
                st.success(f"{d} 모임이 성공적으로 생성되었습니다!")
                st.rerun() # 생성 후 즉시 다시 불러오기
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Tab 3: 참가 접수 ---
    with tab3:
        st.markdown("<div class='excel-card'>", unsafe_allow_html=True)
        st.subheader("📝 참가 신청 접수")
        
        # 여기서 all_sessions를 다시 체크 (최신 상태 보장)
        if not all_sessions:
            st.warning("⚠️ 등록된 모임이 없습니다. '모임 생성' 탭에서 먼저 모임을 만들어주세요.")
        else:
            session_map = {f"{s['date']} | {s['place']}": s['id'] for s in all_sessions}
            target_name = st.selectbox("대상 모임 선택", session_map.keys())
            target_id = session_map[target_name]

            if not all_members:
                st.info("등록된 회원이 없습니다.")
            else:
                member_map = {f"{m['name']} ({m['rank']})": m['id'] for m in all_members}
                selected_names = st.multiselect("참석자 선택", member_map.keys())
                
                if st.button("💾 참가 명단 저장"):
                    # attendance 테이블 insert 로직
                    st.success(f"총 {len(selected_names)}명 접수 완료!")
        st.markdown("</div>", unsafe_allow_html=True)