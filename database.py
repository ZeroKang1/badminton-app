import streamlit as st
from supabase import create_client

# database.py (데이터 파이프라인)
# Supabase와의 통신을 전담합니다. (ID 101부터 시작하는 숫자 체계 반영)

# 본인의 Supabase 설정 정보 (프로젝트 세팅에서 확인 가능)
# SUPABASE_URL = "https://nhczyfpzdyacjuosasaj.supabase.co"
# SUPABASE_KEY = "sb_publishable_WvVdNmJYq3m1AGd1vX-jqQ_TUrSbJo6"

SUPABASE_URL = "https://nhczyfpzdyacjuosasaj.supabase.co"
SUPABASE_KEY = "sb_publishable_WvVdNmJYq3m1AGd1vX-jqQ_TUrSbJo6"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 회원 관리 ---
def get_members():
    res = supabase.table("members").select("*").execute()
    return res.data

# --- 모임(세션) 관리 ---
def create_session(data):
    # data: {'date': '2024-05-20', 'place': 'A체육관', ...}
    return supabase.table("sessions").insert(data).execute()

def get_sessions():
    return supabase.table("sessions").select("*").order("id", desc=True).execute().data

# --- 참석/도착 관리 ---
def get_attendance(session_id):
    # 해당 모임의 참가 접수자 목록
    return supabase.table("attendance").select("*, members(*)").eq("session_id", session_id).execute().data

def update_status(att_id, status):
    # '접수' -> '도착' 등으로 변경
    return supabase.table("attendance").update({"status": status}).eq("id", att_id).execute()