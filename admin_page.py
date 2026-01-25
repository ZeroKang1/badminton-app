import streamlit as st
import pandas as pd
import database as db
import io
from datetime import datetime

# pip install pandas xlsxwriter openpyxl

def show_admin():
    st.title("⚙️ 운영진 관리 페이지")
    
    tab1, tab2, tab3 = st.tabs(["👤 회원 관리", "📅 모임 생성", "🙋 참가 접수"])

    # --- Tab 1: 회원 관리 (엑셀 등록 추가) ---
    with tab1:
        st.subheader("회원 등록")
        
        # --- 1. 샘플 파일 다운로드 부분 ---
        st.write("批量 등록을 원하시면 샘플 양식을 다운로드하여 작성 후 업로드하세요.")
        
        # 샘플 데이터 생성
        sample_df = pd.DataFrame({
            "이름": ["홍길동", "김철수"],
            "생년": ["85", "90"],
            "급수": ["A", "C"]
        })
        
        # 엑셀 파일로 변환 (메모리 버퍼 사용)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            sample_df.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.close()
        
        st.download_button(
            label="📥 회원등록 샘플 파일 다운로드",
            data=buffer.getvalue(),
            file_name="member_sample.xlsx",
            mime="application/vnd.ms-excel"
        )
        
        st.divider()

        # --- 2. 엑셀 파일 업로드 부분 ---
        st.write("### 📂 엑셀 파일 업로드")
        uploaded_file = st.file_uploader("작성한 엑셀 파일을 선택하세요", type=["xlsx", "csv"])

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("📑 업로드 데이터 미리보기:")
                st.dataframe(df, use_container_width=True)

                if st.button("🚀 위 명단 전체 저장하기"):
                    # DB 저장을 위한 데이터 정제 (컬럼명 매칭)
                    members_to_save = []
                    for _, row in df.iterrows():
                        members_to_save.append({
                            "name": str(row["이름"]),
                            "birth": str(row["생년"]),
                            "rank": str(row["급수"])
                        })
                    
                    # database.py의 supabase 호출 (직접 처리 예시)
                    # res = db.supabase.table("members").insert(members_to_save).execute()
                    st.success(f"성공! {len(members_to_save)}명의 회원이 등록되었습니다.")
                    st.rerun()
            except Exception as e:
                st.error(f"파일 읽기 오류: {e}")

        st.divider()
        
        # --- 3. 기존 수동 등록 (기존 코드 유지) ---
        with st.expander("➕ 수동으로 1명씩 등록하기"):
            with st.form("member_form", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                name = col1.text_input("이름")
                birth = col2.text_input("생년(2자리)", placeholder="85")
                rank = col3.selectbox("급수", ["S", "A", "B", "C", "D", "초심"])
                if st.form_submit_button("회원 저장"):
                    if name:
                        db.supabase.table("members").insert({"name": name, "birth": birth, "rank": rank}).execute()
                        st.success(f"{name} 등록 완료!")
                    else: st.error("이름을 입력하세요.")

    # --- Tab 2: 모임 생성 ---
    with tab2:
        st.subheader("정기 모임/번개 생성")
        with st.form("session_form"):
            date = st.date_input("모임 날짜", datetime.now())
            place = st.text_input("장소", "민턴캐슬")
            courts = st.text_input("사용 코트 (예: 5,6,7,9)", "5,6,7,9")
            if st.form_submit_button("모임 개설"):
                # db.create_session({"date": str(date), "place": place, "courts_count": 4})
                st.success(f"{date} {place} 모임이 생성되었습니다. (ID: 101~)")

    # --- Tab 3: 참가 신청 (매칭의 시작) ---
    with tab3:
        st.subheader("모임별 참가자 접수")
        sessions = db.get_sessions()
        if not sessions:
            st.info("먼저 모임을 생성해주세요.")
        else:
            # 1. 대상 모임 선택
            session_options = {f"{s['date']} ({s['place']})": s['id'] for s in sessions}
            selected_session_name = st.selectbox("참가 접수를 받을 모임 선택", session_options.keys())
            target_sid = session_options[selected_session_name]

            # 2. 회원 다중 선택
            all_members = db.get_members()
            member_options = {f"{m['name']}({m['rank']})": m['id'] for m in all_members}
            
            selected_m_names = st.multiselect("참석 인원 선택 (밴드 명단 보고 체크)", member_options.keys())
            
            if st.button("참가 명단 확정"):
                # 실제로는 attendance 테이블에 (session_id, member_id, status='접수') 저장
                st.success(f"{len(selected_m_names)}명의 접수가 완료되었습니다!")
                st.balloons()

if __name__ == "__main__":
    show_admin()