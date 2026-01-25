import streamlit as st
import pandas as pd
import database as db
import io
from datetime import datetime
import match_manager as mm

def show_admin():
    # CSS 스타일 (슬림 & 파스텔 유지)
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        html, body, [data-testid="stAppViewContainer"] { font-family: 'Noto Sans KR', sans-serif; background-color: #f8f9fa; }
        div[data-testid="stColumn"] { padding: 0px 1px !important; }
        .stTextInput input, .stSelectbox div { 
            height: 28px !important; font-size: 12px !important; 
            letter-spacing: -0.5px !important; padding: 0 4px !important;
            border-radius: 4px !important; border: 1px solid #e0e6ed !important;
        }
        .header-row { 
            background-color: #e3f2fd; color: #455a64; padding: 4px; 
            border-radius: 4px; font-weight: bold; font-size: 12px; 
            text-align: center; letter-spacing: -0.8px; margin-bottom: 2px;
        }
        .stButton>button { 
            background-color: #f1f8e9; color: #558b2f; border: 1px solid #dcedc8;
            border-radius: 4px; font-size: 11px; height: 26px; width: 100%;
            letter-spacing: -1px; font-weight: bold;
        }
        .stButton>button:hover { background-color: #dcedc8; }
        /* 삭제 버튼 전용 레드 파스텔 */
        div.stButton > button[kind="primary"] { background-color: #fff1f0; color: #cf1322; border: 1px solid #ffa39e; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏸 운영진 관리 (Final)")

    # [데이터 로드 및 정렬]
    all_members = db.get_members()
    all_sessions = db.get_sessions()
    
    if all_members:
        df_members = pd.DataFrame(all_members).sort_values(by=['group_name', 'name'])
    else:
        df_members = pd.DataFrame(columns=["id", "name", "gender", "birth", "rank", "phone", "group_name", "memo"])

    tab1, tab2, tab3 = st.tabs(["📊 회원명단", "📅 모임관리", "📝 참가접수"])

    # --- [Tab 1: 회원명단 관리] ---
    with tab1:
        c_title, c_filter, c_add, c_bulk, c_del, c_save = st.columns([1.5, 1.2, 0.7, 0.7, 0.7, 0.7])
        
        with c_title: st.caption(f"👥 총 {len(df_members)}명")
        with c_filter:
            unique_groups = sorted(list(df_members["group_name"].unique())) if not df_members.empty else []
            selected_group = st.selectbox("필터", ["전체"] + unique_groups, label_visibility="collapsed")
        
        # 목록 데이터 준비
        display_df = df_members if selected_group == "전체" else df_members[df_members["group_name"] == selected_group]
        
        # 버튼 동작 정의
        with c_add: 
            if st.button("➕추가"): st.session_state.show_add = True
        with c_bulk:
            with st.popover("📂일괄"):
                st.caption("Excel 파일 관리")
                # 샘플 다운로드 및 업로드 로직 (기존 유지)
        
        # [목록 헤더]
        h = st.columns([1.0, 1.2, 1.2, 0.8, 0.8, 1.8, 1.5, 2.5])
        labels = ["선택", "이름", "성별", "생년", "급수", "연락처", "그룹명", "메모"]
        for i, label in enumerate(labels):
            h[i].markdown(f'<div class="header-row">{label}</div>', unsafe_allow_html=True)

        # [데이터 리스트 및 수정 데이터 수집]
        updated_data = []
        selected_ids = []

        for _, row in display_df.iterrows():
            r = st.columns([1.0, 1.2, 1.2, 0.8, 0.8, 1.8, 1.5, 2.5])
            
            # 1. 체크박스 (삭제용)
            is_selected = r[0].checkbox("", key=f"sel_{row['id']}", label_visibility="collapsed", help=f"ID: {row['id']}")
            if is_selected: selected_ids.append(row['id'])
            
            # 2. 인라인 수정 입력창
            u_name = r[1].text_input("", value=row['name'], key=f"n_{row['id']}", label_visibility="collapsed")
            u_gen = r[2].selectbox("", ["남", "여"], index=0 if row['gender']=="남" else 1, key=f"g_{row['id']}", label_visibility="collapsed")
            u_birth = r[3].text_input("", value=row['birth'], key=f"b_{row['id']}", label_visibility="collapsed")
            u_rank = r[4].text_input("", value=row['rank'], key=f"r_{row['id']}", label_visibility="collapsed")
            u_phone = r[5].text_input("", value=row['phone'], key=f"p_{row['id']}", label_visibility="collapsed")
            u_group = r[6].text_input("", value=row['group_name'], key=f"gn_{row['id']}", label_visibility="collapsed")
            u_memo = r[7].text_input("", value=row['memo'], key=f"m_{row['id']}", label_visibility="collapsed")
            
            # 수정된 내용이 있다면 리스트에 추가 (id 기준)
            updated_data.append({
                "id": row['id'], "name": u_name, "gender": u_gen, "birth": u_birth, 
                "rank": u_rank, "phone": u_phone, "group_name": u_group, "memo": u_memo
            })

        # [삭제 및 수정 실행 버튼]
        with c_del:
            if st.button("🗑️삭제", type="primary"):
                if selected_ids:
                    db.supabase.table("members").delete().in_("id", selected_ids).execute()
                    st.success(f"{len(selected_ids)}명 삭제 완료")
                    st.rerun()
                else: st.warning("대상을 선택하세요")

        with c_save:
            if st.button("💾수정"):
                for data in updated_data:
                    # 실제 수정된 값만 업데이트 하는 것이 좋으나, 편의상 전체 upsert 처리
                    db.supabase.table("members").upsert(data).execute()
                st.success("변경사항이 저장되었습니다.")
                st.rerun()

        # 신규 추가 행 로직 (기존 유지)
        if st.session_state.get("show_add"):
            st.markdown("---")
            st.info("✨ 신규 회원 정보를 입력하세요")
            ra = st.columns([1.0, 1.2, 1.2, 0.8, 0.8, 1.8, 1.5, 2.5])
            new_n = ra[1].text_input("이름", key="new_n")
            new_g = ra[2].selectbox("성별", ["남", "여"], key="new_g")
            new_b = ra[3].text_input("생년", key="new_b")
            new_r = ra[4].text_input("급수", key="new_r")
            new_p = ra[5].text_input("연락처", key="new_p")
            new_gn = ra[6].text_input("그룹명", key="new_gn")
            new_m = ra[7].text_input("메모", key="new_m")
            if st.button("💾 회원 저장"):
                db.supabase.table("members").insert({"name":new_n,"gender":new_g,"birth":new_b,"rank":new_r,"phone":new_p,"group_name":new_gn,"memo":new_m}).execute()
                st.session_state.show_add = False
                st.rerun()

    # --- [Tab 2: 모임 생성] ---
    with tab2:
        with st.form("session_form"): # 기존 이름 그대로 쓰세요!
            st.subheader("🗓️ 새 정기 모임/번개 개설")
            col1, col2 = st.columns(2)
            d = col1.date_input("모임 날짜", datetime.now())
            p = col2.text_input("장소", "영등포다목적체육관")
            
            # --- 여기 이 한 줄만 추가하면 match_manager와 연동됩니다! ---
            g = col1.text_input("소속 그룹명", value="여민소") 
            # --------------------------------------------------------

            c = col2.number_input("사용 코트 수", 1, 10, 4)
            t = col1.text_input("코트 번호", "5,6,7,9")
            
            if st.form_submit_button("✅ 모임 생성 및 확정"):
                # 데이터 보낼 때 g(그룹명)만 추가해주면 끝!
                db.create_session({
                    "title": f"{d} {p} 모임",
                    "date": str(d), 
                    "place": p, 
                    "group_name": g, # 이 값이 들어가야 Tab 3에서 필터링이 됩니다.
                    "courts_count": c, 
                    "courts_names": t
                })
                st.success("생성 완료!")
                st.rerun()

    # --- [Tab 3: 참가 접수] ---
    with tab3:
        st.markdown("<div class='excel-card'>", unsafe_allow_html=True)
        all_sessions = db.get_sessions()
        if not all_sessions:
            st.warning("📅 모임을 먼저 생성해 주세요 (Tab 2)")
        else:
            # 모임 선택
            s_map = {f"{s['date']} | {s['place']}": s['id'] for s in all_sessions}
            sel_s_name = st.selectbox("접수할 모임 선택", s_map.keys())
            sel_s_id = s_map[sel_s_name]
            
            # 🔗 새 파일의 기능을 연결!
            mm.show_attendance_manager(sel_s_id)
        st.markdown("</div>", unsafe_allow_html=True)