import streamlit as st
from supabase import create_client

# 본인의 Supabase 설정 정보 (프로젝트 세팅에서 확인 가능)
SUPABASE_URL = "https://nhczyfpzdyacjuosasaj.supabase.co"
SUPABASE_KEY = "sb_publishable_WvVdNmJYq3m1AGd1vX-jqQ_TUrSbJo6"

# DB 연결 클라이언트 생성
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_members():
    """전체 회원 명단 가져오기"""
    try:
        res = supabase.table("members").select("*").execute()
        return res.data
    except Exception as e:
        st.error(f"회원 명단 로드 실패: {e}")
        return []

def get_sessions():
    """모임 목록 가져오기"""
    res = supabase.table("sessions").select("*").order("date", desc=True).execute()
    return res.data

def save_match_result(data):
    """경기 결과 영구 저장"""
    return supabase.table("match_results").insert(data).execute()

def get_history(session_id):
    """오늘의 경기 이력 가져오기"""
    res = supabase.table("match_results").select("*").eq("session_id", session_id).order("created_at", desc=True).execute()
    return res.data