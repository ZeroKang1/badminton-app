import streamlit as st
from supabase import create_client
from datetime import datetime, date
from functools import lru_cache

# ============================================================
# Supabase 연결 설정
# ============================================================
SUPABASE_URL = "https://nhczyfpzdyacjuosasaj.supabase.co"
SUPABASE_KEY = "sb_publishable_WvVdNmJYq3m1AGd1vX-jqQ_TUrSbJo6"

@st.cache_resource
def get_supabase_client():
    """Supabase 클라이언트 싱글톤"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# ============================================================
# 캐시 관리
# ============================================================
def clear_cache():
    """모든 캐시 클리어"""
    st.cache_data.clear()

# ============================================================
# 회원 관리 (Members) - 캐싱 적용
# ============================================================
@st.cache_data(ttl=60)  # 60초 캐시
def get_members(group_name=None):
    """회원 목록 조회 (그룹 필터링 옵션)"""
    query = supabase.table("members").select("*").is_("deleted_at", "null")
    if group_name and group_name != "전체":
        query = query.eq("group_name", group_name)
    return query.order("name").execute().data or []

def get_member_by_id(member_id):
    """회원 상세 조회"""
    res = supabase.table("members").select("*").eq("id", member_id).single().execute()
    return res.data

def create_member(data):
    """회원 등록"""
    clear_cache()
    return supabase.table("members").insert(data).execute()

def update_member(member_id, data):
    """회원 수정"""
    clear_cache()
    return supabase.table("members").update(data).eq("id", member_id).execute()

def delete_member(member_id):
    """회원 삭제 (soft delete)"""
    clear_cache()
    return supabase.table("members").update({"deleted_at": datetime.now().isoformat()}).eq("id", member_id).execute()

def format_player_name(member):
    """선수 표기 형식: 이름생년급수 (예: 홍길동85A)"""
    if not member:
        return ""
    name = member.get('name', '')
    birth = str(member.get('birth', ''))[-2:] if member.get('birth') else ''
    rank = member.get('rank', '') or ''
    return f"{name}{birth}{rank}"

# ============================================================
# 모임 관리 (Sessions) - 캐싱 적용
# ============================================================
@st.cache_data(ttl=30)  # 30초 캐시
def get_sessions(limit=20):
    """모임 목록 조회 (최신순)"""
    return supabase.table("sessions").select("*").order("date", desc=True).limit(limit).execute().data or []

@st.cache_data(ttl=30)
def get_session_by_id(session_id):
    """모임 상세 조회"""
    res = supabase.table("sessions").select("*").eq("id", session_id).single().execute()
    return res.data

def create_session(data):
    """모임 생성"""
    clear_cache()
    return supabase.table("sessions").insert(data).execute()

def update_session(session_id, data):
    """모임 수정"""
    clear_cache()
    return supabase.table("sessions").update(data).eq("id", session_id).execute()

def delete_session(session_id):
    """모임 삭제"""
    clear_cache()
    return supabase.table("sessions").delete().eq("id", session_id).execute()

# ============================================================
# 참가자 관리 (Participants) - 캐싱 적용
# ============================================================
"""
status 값:
- registered: 참가접수 (온라인 신청)
- confirmed: 모임참석신청 확정
- checked_in: 출석체크 완료 (현장 도착)
- waiting: 코트대기 (대기열에 배치됨)
- playing: 게임중 (코트에서 경기중)
- resting: 휴식중
- left: 퇴장
- cancelled: 취소
"""

@st.cache_data(ttl=10)  # 10초 캐시 (라이브 데이터)
def get_participants(session_id, status=None):
    """참가자 목록 조회 (모임별, 상태 필터링 옵션)"""
    query = supabase.table("participants").select("*, members!participants_member_id_fkey(*)").eq("session_id", session_id)
    if status:
        if isinstance(status, list):
            query = query.in_("status", status)
        else:
            query = query.eq("status", status)
    return query.execute().data or []

def get_participant_by_id(participant_id):
    """참가자 상세 조회"""
    res = supabase.table("participants").select("*, members!participants_member_id_fkey(*)").eq("id", participant_id).single().execute()
    return res.data

def create_participant(session_id, member_id, status="registered"):
    """참가자 등록"""
    clear_cache()
    data = {
        "session_id": session_id,
        "member_id": member_id,
        "status": status,
        "entry_time": datetime.now().strftime("%H:%M")
    }
    return supabase.table("participants").insert(data).execute()

def update_participant_status(participant_id, status, **kwargs):
    """참가자 상태 변경"""
    clear_cache()
    data = {"status": status, **kwargs}
    return supabase.table("participants").update(data).eq("id", participant_id).execute()

def delete_participant(participant_id):
    """참가자 삭제"""
    clear_cache()
    return supabase.table("participants").delete().eq("id", participant_id).execute()

def bulk_update_participants(participant_ids, status):
    """참가자 일괄 상태 변경"""
    clear_cache()
    return supabase.table("participants").update({"status": status}).in_("id", participant_ids).execute()

# ============================================================
# 경기 관리 (Matches)
# ============================================================
@st.cache_data(ttl=10)
def get_matches(session_id):
    """경기 목록 조회"""
    return supabase.table("matches").select("*").eq("session_id", session_id).order("match_order").execute().data or []

def get_active_matches(session_id):
    """진행중인 경기 조회 (종료되지 않은 경기)"""
    return supabase.table("matches").select("*").eq("session_id", session_id).is_("actual_end", "null").execute().data or []

def create_match(session_id, court_num, team_a_p1, team_a_p2, team_b_p1, team_b_p2):
    """경기 생성"""
    clear_cache()
    matches = get_matches.__wrapped__(session_id)  # 캐시 우회
    next_order = len(matches) + 1

    data = {
        "session_id": session_id,
        "match_order": next_order,
        "court_num": court_num,
        "team_a_p1": team_a_p1,
        "team_a_p2": team_a_p2,
        "team_b_p1": team_b_p1,
        "team_b_p2": team_b_p2,
        "actual_start": datetime.now().isoformat()
    }
    return supabase.table("matches").insert(data).execute()

def end_match(match_id, score_a=0, score_b=0):
    """경기 종료"""
    clear_cache()
    data = {
        "actual_end": datetime.now().isoformat(),
        "score_a": score_a,
        "score_b": score_b
    }
    return supabase.table("matches").update(data).eq("id", match_id).execute()

def update_match(match_id, data):
    """경기 정보 수정"""
    clear_cache()
    return supabase.table("matches").update(data).eq("id", match_id).execute()

# ============================================================
# 대기열 관리 (Court Queue) - 세션 상태 기반
# ============================================================
def get_court_queue(session_id):
    """대기열 조회 (waiting 상태인 참가자)"""
    return get_participants(session_id, status="waiting")

def assign_to_queue(participant_id):
    """대기열에 배정"""
    clear_cache()
    return supabase.table("participants").update({"status": "waiting"}).eq("id", participant_id).execute()

def assign_to_court(participant_ids):
    """코트에 배정 (4명) - status만 변경"""
    clear_cache()
    return supabase.table("participants").update({
        "status": "playing"
    }).in_("id", participant_ids).execute()

def release_from_court(participant_ids):
    """코트에서 해제 (경기 종료)"""
    clear_cache()
    return supabase.table("participants").update({
        "status": "checked_in"
    }).in_("id", participant_ids).execute()

# ============================================================
# 경기 결과 관리 (Match Results)
# ============================================================
def save_match_result(session_id, court_name, team_a_players, team_b_players,
                      score_a=0, score_b=0, start_time=None, end_time=None):
    """경기 결과 저장"""
    clear_cache()
    data = {
        "session_id": session_id,
        "court_name": court_name,
        "team_a_players": team_a_players,
        "team_b_players": team_b_players,
        "score_a": score_a,
        "score_b": score_b,
        "start_time": start_time,
        "end_time": end_time
    }
    return supabase.table("match_results").insert(data).execute()

@st.cache_data(ttl=30)
def get_match_results(session_id):
    """경기 결과 조회"""
    return supabase.table("match_results").select("*").eq("session_id", session_id).order("created_at").execute().data or []

# ============================================================
# 통계 및 리포트 - 캐싱 적용
# ============================================================
@st.cache_data(ttl=30)
def get_session_stats(session_id):
    """모임 통계 조회"""
    participants = get_participants(session_id)
    matches = get_match_results(session_id)

    total_participants = len(participants)
    male_count = sum(1 for p in participants if p.get('members', {}).get('gender') == '남')
    female_count = total_participants - male_count
    total_matches = len(matches)

    return {
        "total_participants": total_participants,
        "male_count": male_count,
        "female_count": female_count,
        "total_matches": total_matches
    }
