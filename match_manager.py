import streamlit as st
import database as db

def show_attendance_manager(selected_session_id):
    """
    모임의 소속그룹 회원만 필터링하여 '이름+생년+급수' 형태로 체크박스 접수
    (DB 테이블명을 'participants'로 수정 반영)
    """
    # 1. 선택된 모임 정보 가져오기
    try:
        session_res = db.supabase.table("sessions").select("*").eq("id", selected_session_id).single().execute()
        if not session_res.data:
            st.warning("모임 정보를 불러올 수 없습니다.")
            return
        
        session = session_res.data
        target_group = session.get("group_name", "전체")
        st.info(f"📍 **{session['date']} / {session['place']}** ({target_group} 모임)")

        # 2. 해당 그룹 회원 필터링
        query = db.supabase.table("members").select("id", "name", "birth", "rank", "group_name")
        if target_group and target_group != "전체":
            query = query.eq("group_name", target_group)
        
        members_res = query.order("name").execute()
        members = members_res.data if members_res.data else []

        if not members:
            st.error(f"'{target_group}' 그룹에 등록된 회원이 없습니다.")
            return

        # 3. 현재 이미 접수된 명단 가져오기 (테이블명 수정: attendance -> participants)
        current_att = db.supabase.table("participants").select("member_id").eq("session_id", selected_session_id).execute()
        attended_ids = [a['member_id'] for a in current_att.data] if current_att.data else []

        # 4. 참가 접수 UI
        st.write("---")
        st.caption("✅ 참석자는 체크해 주세요. (이름생년급수)")
        
        cols = st.columns(3)
        new_selected_ids = []

        for idx, m in enumerate(members):
            # 표시 형식: 이름생년급수 (예: 홍길동85A)
            display_text = f"{m['name']}{m.get('birth','')}{m.get('rank','')}"
            is_checked = m['id'] in attended_ids
            
            with cols[idx % 3]:
                if st.checkbox(display_text, key=f"att_{m['id']}", value=is_checked):
                    new_selected_ids.append(m['id'])

        st.write("---")
        
        # 5. 저장 버튼
        col_btn, col_count = st.columns([1, 1])
        with col_count:
            st.metric("현재 접수 인원", f"{len(new_selected_ids)} 명")
            
        if col_btn.button("💾 참가 명단 최종 확정", use_container_width=True, type="primary"):
            # 테이블명 수정: attendance -> participants
            db.supabase.table("participants").delete().eq("session_id", selected_session_id).execute()
            
            if new_selected_ids:
                insert_data = [{"session_id": selected_session_id, "member_id": mid} for mid in new_selected_ids]
                db.supabase.table("participants").insert(insert_data).execute()
            
            st.success("접수 완료! 상황실에 명단이 반영되었습니다.")
            st.balloons()

    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")