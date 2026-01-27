import streamlit as st
import pandas as pd
import database as db
from datetime import datetime

# ============================================================
# 설정
# ============================================================
APP_NAME = "소꾹"  # 배드민턴 소모임 위꾹
DEFAULT_GROUP = "소꾹"

def show_admin():
    """운영진 관리 페이지 - 최적화된 엑셀 스타일"""

    # CSS 스타일
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600&display=swap');
        * { font-family: 'Noto Sans KR', sans-serif; }
        .stApp { background-color: #f5f7fa; }
        .admin-header {
            background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
            color: white; padding: 15px 20px; border-radius: 10px;
            margin-bottom: 15px; box-shadow: 0 4px 12px rgba(25,118,210,0.3);
        }
        .stat-box {
            background: white; border-radius: 8px; padding: 12px 15px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08); border-left: 4px solid #1976d2;
        }
        .stat-num { font-size: 24px; font-weight: 700; color: #1976d2; }
        .stat-label { font-size: 11px; color: #666; }
        .section-title {
            font-size: 15px; font-weight: 600; color: #333;
            padding: 8px 0; border-bottom: 2px solid #1976d2; margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 헤더
    st.markdown(f"""
    <div class="admin-header">
        <span style="font-size:22px; font-weight:700;">⚙️ {APP_NAME} 운영관리</span>
        <span style="margin-left:15px; opacity:0.8; font-size:13px;">시스템 설정 및 데이터 관리</span>
    </div>
    """, unsafe_allow_html=True)

    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 회원", "📅 모임", "📝 접수", "📈 보고"])

    with tab1:
        render_member_tab()
    with tab2:
        render_session_tab()
    with tab3:
        render_attendance_tab()
    with tab4:
        render_report_tab()


def render_member_tab():
    """회원 관리 탭 - 최적화"""

    members = db.get_members()
    df = pd.DataFrame(members) if members else pd.DataFrame()

    # 통계
    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(df)}</div><div class="stat-label">총 회원</div></div>', unsafe_allow_html=True)
    with c2:
        male = len(df[df['gender'] == '남']) if not df.empty else 0
        st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#1565c0;">{male}</div><div class="stat-label">남성</div></div>', unsafe_allow_html=True)
    with c3:
        female = len(df) - male if not df.empty else 0
        st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#c62828;">{female}</div><div class="stat-label">여성</div></div>', unsafe_allow_html=True)
    with c4:
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("➕ 신규등록", use_container_width=True):
                st.session_state.show_add = True
        with bc2:
            if st.button("🔄 새로고침", use_container_width=True):
                db.clear_cache()
                st.rerun()

    st.markdown("---")

    # 필터
    fc1, fc2, fc3 = st.columns([1, 1, 2])
    with fc1:
        groups = sorted(df['group_name'].dropna().unique().tolist()) if not df.empty else []
        filter_g = st.selectbox("그룹", ["전체"] + groups, key="fg")
    with fc2:
        filter_s = st.selectbox("성별", ["전체", "남", "여"], key="fs")
    with fc3:
        search = st.text_input("검색", placeholder="이름 검색...", key="search")

    # 필터 적용
    fdf = df.copy() if not df.empty else pd.DataFrame()
    if not fdf.empty:
        if filter_g != "전체":
            fdf = fdf[fdf['group_name'] == filter_g]
        if filter_s != "전체":
            fdf = fdf[fdf['gender'] == filter_s]
        if search:
            fdf = fdf[fdf['name'].str.contains(search, na=False)]

    # 테이블
    st.markdown(f'<div class="section-title">회원 목록 ({len(fdf)}명)</div>', unsafe_allow_html=True)

    if not fdf.empty:
        cols = ['id', 'name', 'gender', 'birth', 'rank', 'phone', 'group_name', 'memo']
        ddf = fdf[cols].copy()
        ddf.columns = ['ID', '이름', '성별', '생년', '급수', '연락처', '그룹', '메모']

        # 수정 모드 선택
        edit_mode = st.radio("수정 모드", ["조회만", "1건 수정", "N건 일괄수정"], horizontal=True, label_visibility="collapsed")

        if edit_mode == "조회만":
            st.dataframe(ddf, use_container_width=True, hide_index=True, height=400)

        elif edit_mode == "1건 수정":
            # 회원 선택
            member_opts = {f"{m['name']} ({m.get('birth','')}{m.get('rank','')})": m['id'] for m in fdf.to_dict('records')}
            selected_name = st.selectbox("수정할 회원 선택", list(member_opts.keys()))
            selected_id = member_opts[selected_name]
            selected_member = fdf[fdf['id'] == selected_id].iloc[0].to_dict()

            with st.form("edit_single_form"):
                st.markdown(f"**{selected_member['name']}** 정보 수정")
                r1c1, r1c2, r1c3, r1c4 = st.columns(4)
                new_name = r1c1.text_input("이름", value=selected_member.get('name', ''))
                new_gender = r1c2.selectbox("성별", ["남", "여"], index=0 if selected_member.get('gender') == '남' else 1)
                new_birth = r1c3.text_input("생년", value=str(selected_member.get('birth', '') or ''))
                rank_opts = ["A", "B", "C", "D", "초심"]
                rank_idx = rank_opts.index(selected_member.get('rank', 'C')) if selected_member.get('rank') in rank_opts else 2
                new_rank = r1c4.selectbox("급수", rank_opts, index=rank_idx)

                r2c1, r2c2, r2c3 = st.columns(3)
                new_phone = r2c1.text_input("연락처", value=selected_member.get('phone', '') or '')
                new_group = r2c2.text_input("그룹", value=selected_member.get('group_name', '') or '')
                new_memo = r2c3.text_input("메모", value=selected_member.get('memo', '') or '')

                col_save, col_del = st.columns(2)
                if col_save.form_submit_button("💾 저장", type="primary"):
                    db.update_member(selected_id, {
                        "name": new_name, "gender": new_gender, "birth": new_birth,
                        "rank": new_rank, "phone": new_phone, "group_name": new_group, "memo": new_memo
                    })
                    st.success(f"'{new_name}' 수정 완료!")
                    db.clear_cache()
                    st.rerun()
                if col_del.form_submit_button("🗑️ 삭제", type="secondary"):
                    db.delete_member(selected_id)
                    st.warning(f"'{selected_member['name']}' 삭제됨")
                    db.clear_cache()
                    st.rerun()

        elif edit_mode == "N건 일괄수정":
            st.info("일괄 수정할 회원을 선택하세요")
            # 멀티셀렉트로 선택
            member_opts = {f"{m['name']} ({m.get('birth','')}{m.get('rank','')})": m['id'] for m in fdf.to_dict('records')}
            selected_names = st.multiselect("회원 선택", list(member_opts.keys()))
            selected_ids = [member_opts[n] for n in selected_names]

            if selected_ids:
                st.write(f"**선택됨: {len(selected_ids)}명**")
                with st.form("edit_bulk_form"):
                    st.markdown("아래 값을 입력하면 선택한 회원 전체에 적용됩니다 (빈칸은 변경 안함)")
                    bc1, bc2, bc3 = st.columns(3)
                    bulk_rank = bc1.selectbox("급수 변경", ["변경안함", "A", "B", "C", "D", "초심"])
                    bulk_group = bc2.text_input("그룹 변경", placeholder="입력시 일괄 적용")
                    bulk_action = bc3.selectbox("일괄 작업", ["선택", "삭제"])

                    if st.form_submit_button("✅ 일괄 적용", type="primary"):
                        if bulk_action == "삭제":
                            for mid in selected_ids:
                                db.delete_member(mid)
                            st.warning(f"{len(selected_ids)}명 삭제됨")
                        else:
                            update_data = {}
                            if bulk_rank != "변경안함":
                                update_data["rank"] = bulk_rank
                            if bulk_group:
                                update_data["group_name"] = bulk_group
                            if update_data:
                                for mid in selected_ids:
                                    db.update_member(mid, update_data)
                                st.success(f"{len(selected_ids)}명 수정 완료!")
                        db.clear_cache()
                        st.rerun()
    else:
        st.info("회원이 없습니다.")

    # 신규 등록 폼
    if st.session_state.get("show_add"):
        with st.expander("✨ 신규 회원 등록", expanded=True):
            with st.form("add_form"):
                r1c1, r1c2, r1c3, r1c4 = st.columns(4)
                name = r1c1.text_input("이름*")
                gender = r1c2.selectbox("성별", ["남", "여"])
                birth = r1c3.text_input("생년")
                rank = r1c4.selectbox("급수", ["A", "B", "C", "D", "초심"])

                r2c1, r2c2, r2c3 = st.columns(3)
                phone = r2c1.text_input("연락처")
                group = r2c2.text_input("그룹", value=DEFAULT_GROUP)
                memo = r2c3.text_input("메모")

                if st.form_submit_button("등록", type="primary"):
                    if name:
                        db.create_member({
                            "name": name, "gender": gender, "birth": birth,
                            "rank": rank, "phone": phone, "group_name": group, "memo": memo
                        })
                        st.success(f"'{name}' 등록 완료!")
                        st.session_state.show_add = False
                        st.rerun()


def render_session_tab():
    """모임 관리 탭"""

    sessions = db.get_sessions(limit=20)

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown('<div class="section-title">모임 목록</div>', unsafe_allow_html=True)
    with c2:
        if st.button("➕ 새 모임", use_container_width=True):
            st.session_state.show_session = True

    if sessions:
        data = [{
            "ID": s['id'],
            "날짜": s.get('date', ''),
            "장소": s.get('location', ''),
            "코트": s.get('courts_num', 0),
            "상태": "🟢" if s.get('date') == str(datetime.now().date()) else "⚪"
        } for s in sessions]

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("모임이 없습니다.")

    # 새 모임 생성
    if st.session_state.get("show_session"):
        with st.expander("🗓️ 새 모임 생성", expanded=True):
            with st.form("session_form"):
                c1, c2 = st.columns(2)
                s_date = c1.date_input("날짜", datetime.now())
                s_loc = c2.text_input("장소", "영등포다목적체육관")
                s_courts = c1.number_input("코트 수", 1, 10, 4)
                s_names = c2.text_input("코트 번호", "5,6,7,9")
                s_group = st.text_input("그룹", DEFAULT_GROUP)

                if st.form_submit_button("생성", type="primary"):
                    db.create_session({
                        "title": f"{s_date} {s_loc}",
                        "date": str(s_date),
                        "location": s_loc,
                        "group_name": s_group,
                        "courts_num": s_courts,
                        "courts_names": s_names
                    })
                    st.success("모임 생성 완료!")
                    st.session_state.show_session = False
                    st.rerun()


def render_attendance_tab():
    """참가 접수 탭 - 최적화"""

    sessions = db.get_sessions(limit=10)

    if not sessions:
        st.warning("모임을 먼저 생성하세요.")
        return

    # 모임 선택
    opts = {f"{s['date']} {s.get('location', '')[:10]}": s['id'] for s in sessions}
    sel = st.selectbox("모임", list(opts.keys()))
    session_id = opts[sel]

    session_info = db.get_session_by_id(session_id)
    target_group = session_info.get('group_name', '전체')

    st.info(f"📍 {session_info['date']} / {session_info.get('location', '')} ({target_group})")

    # 회원 로드
    members = db.get_members(group_name=target_group if target_group != "전체" else None)

    if not members:
        st.error(f"'{target_group}' 그룹에 회원이 없습니다.")
        return

    # 현재 접수자
    current = db.get_participants(session_id)
    attended_ids = {p['member_id'] for p in current}

    st.markdown("---")
    st.markdown(f'<div class="section-title">참가 접수 ({len(attended_ids)}/{len(members)}명)</div>', unsafe_allow_html=True)

    # 멀티셀렉트로 간소화 (성능 개선)
    member_opts = {m['id']: f"{'🔵' if m.get('gender')=='남' else '🔴'} {db.format_player_name(m)}" for m in members}

    selected = st.multiselect(
        "참가자 선택",
        options=list(member_opts.keys()),
        default=list(attended_ids),
        format_func=lambda x: member_opts.get(x, str(x)),
        label_visibility="collapsed"
    )

    st.markdown("---")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.metric("선택 인원", f"{len(selected)}명")
    with c2:
        if st.button("💾 참가 명단 확정", type="primary", use_container_width=True):
            # 기존 삭제 후 새로 등록
            db.supabase.table("participants").delete().eq("session_id", session_id).execute()

            if selected:
                data = [{"session_id": session_id, "member_id": mid, "status": "checked_in"} for mid in selected]
                db.supabase.table("participants").insert(data).execute()

            db.clear_cache()
            st.success("참가 명단 확정!")
            st.balloons()


def render_report_tab():
    """결과 보고 탭"""

    sessions = db.get_sessions(limit=20)

    if not sessions:
        st.warning("보고서 생성할 모임이 없습니다.")
        return

    opts = {f"{s['date']} {s.get('location', '')[:10]}": s['id'] for s in sessions}
    sel = st.selectbox("모임", list(opts.keys()), key="report_sel")
    session_id = opts[sel]

    session_info = db.get_session_by_id(session_id)
    stats = db.get_session_stats(session_id)
    participants = db.get_participants(session_id)
    results = db.get_match_results(session_id)

    # 통계
    st.markdown('<div class="section-title">📋 모임 정보</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["total_participants"]}</div><div class="stat-label">참석</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#1565c0;">{stats["male_count"]}</div><div class="stat-label">남성</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#c62828;">{stats["female_count"]}</div><div class="stat-label">여성</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#388e3c;">{stats["total_matches"]}</div><div class="stat-label">경기</div></div>', unsafe_allow_html=True)

    # 참석자
    st.markdown("---")
    st.markdown('<div class="section-title">👥 참석자 명단</div>', unsafe_allow_html=True)

    if participants:
        data = [{
            "#": i+1,
            "선수": db.format_player_name(p.get('members', {})),
            "성별": p.get('members', {}).get('gender', ''),
            "급수": p.get('members', {}).get('rank', ''),
            "상태": p.get('status', '')
        } for i, p in enumerate(participants)]

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    # 경기 기록
    st.markdown("---")
    st.markdown('<div class="section-title">🎮 경기 기록</div>', unsafe_allow_html=True)

    if results:
        data = [{
            "#": i+1,
            "코트": m.get('court_name', ''),
            "Team A": ", ".join(m.get('team_a_players', []) or []),
            "Team B": ", ".join(m.get('team_b_players', []) or []),
            "시작": m.get('start_time', ''),
            "종료": m.get('end_time', '')
        } for i, m in enumerate(results)]

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("기록된 경기가 없습니다.")

    # 내보내기
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📥 Excel 다운로드", use_container_width=True):
            st.toast("Excel 다운로드 준비중...")
    with c2:
        if st.button("📤 공유", use_container_width=True):
            st.toast("공유 기능 준비중...")


if __name__ == "__main__":
    show_admin()
