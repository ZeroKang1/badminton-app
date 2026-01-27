import streamlit as st
import streamlit.components.v1 as components
import database as db
from datetime import datetime
import time

# ============================================================
# 설정
# ============================================================
APP_NAME = "소꾹"  # 배드민턴 소모임 위꾹
REFRESH_INTERVAL = 10  # 자동 새로고침 간격 (초)

# ============================================================
# CSS 스타일 정의 (3가지 모드) - 최적화
# ============================================================

def get_magnet_style():
    """자석모드 CSS"""
    return """<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');
* { font-family: 'Noto Sans KR', sans-serif; }
.refresh-info { position: fixed; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: #4caf50; padding: 5px 12px; border-radius: 15px; font-size: 11px; z-index: 1000; }
    :root {
        --board-bg: #2d5a27;
        --court-bg: #1e3d1a;
        --male-color: #1565c0;
        --female-color: #c62828;
    }
    .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
    .live-header {
        background: linear-gradient(90deg, var(--board-bg), #1e4620);
        color: white; padding: 12px 20px; border-radius: 10px;
        margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .court-box {
        background: var(--court-bg); border: 2px solid #4caf50;
        border-radius: 12px; padding: 12px; margin: 5px;
        min-height: 200px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .court-title { color: #81c784; font-size: 16px; font-weight: 700; text-align: center; }
    .court-timer { color: #ffeb3b; font-size: 13px; text-align: center; font-family: monospace; }
    .magnet {
        display: inline-flex; flex-direction: column; align-items: center;
        justify-content: center; width: 75px; height: 55px; border-radius: 8px;
        margin: 3px; font-weight: 600; box-shadow: 2px 2px 6px rgba(0,0,0,0.4);
        border: 2px solid rgba(255,255,255,0.3);
    }
    .magnet-male { background: linear-gradient(145deg, #42a5f5, #1565c0); color: white; }
    .magnet-female { background: linear-gradient(145deg, #ef5350, #c62828); color: white; }
    .magnet-empty { background: rgba(255,255,255,0.1); border: 2px dashed rgba(255,255,255,0.3); color: rgba(255,255,255,0.4); }
    .magnet-name { font-size: 12px; font-weight: 700; }
    .magnet-info { font-size: 10px; opacity: 0.9; }
    .vs-text { color: #ffeb3b; font-size: 14px; font-weight: bold; text-align: center; margin: 8px 0; }
    .queue-box {
        background: linear-gradient(145deg, #455a64, #37474f);
        border: 2px solid #607d8b; border-radius: 10px; padding: 10px; margin: 5px;
        min-height: 140px;
    }
    .queue-title { color: #90caf9; font-size: 13px; font-weight: 600; text-align: center; }
    .pool-box {
        background: linear-gradient(145deg, #263238, #1c252a);
        border-radius: 10px; padding: 12px; margin: 8px 0;
    }
    .pool-title { color: #80cbc4; font-size: 13px; font-weight: 600; border-bottom: 1px solid #37474f; padding-bottom: 8px; margin-bottom: 10px; }
    </style>
    """

def get_list_style():
    """리스트모드 CSS"""
    return """<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');
* { font-family: 'Noto Sans KR', sans-serif; }
.refresh-info { position: fixed; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: #4caf50; padding: 5px 12px; border-radius: 15px; font-size: 11px; z-index: 1000; }
.stApp { background-color: #f5f5f5; }
.live-header { background: white; color: #333; padding: 12px 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #1976d2; }
.section-box { background: white; border-radius: 8px; padding: 15px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.chip-male { background: #e3f2fd; color: #1565c0; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 2px; display: inline-block; }
.chip-female { background: #fce4ec; color: #c62828; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 2px; display: inline-block; }
</style>"""

def get_led_style():
    """전광판모드 CSS"""
    return """<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif; }
.refresh-info { position: fixed; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: #4caf50; padding: 5px 12px; border-radius: 15px; font-size: 11px; z-index: 1000; }
.stApp { background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%); }
.live-header { background: #000; color: #00ff00; padding: 15px 25px; border: 2px solid #00ff00; margin-bottom: 20px; font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px #00ff00; box-shadow: 0 0 20px rgba(0,255,0,0.3); }
.led-court { background: #000; border: 3px solid #00ff00; border-radius: 5px; padding: 15px; margin: 8px; box-shadow: 0 0 20px rgba(0,255,0,0.2); }
.led-title { font-family: 'Orbitron'; color: #00ff00; font-size: 20px; text-align: center; text-shadow: 0 0 10px #00ff00; }
.led-timer { font-family: 'Orbitron'; color: #ff0000; font-size: 28px; text-align: center; text-shadow: 0 0 15px #ff0000; }
.led-player { background: #111; border: 2px solid #00ff00; padding: 8px; margin: 4px; text-align: center; font-weight: 700; }
.led-male { color: #00bfff; border-color: #00bfff; text-shadow: 0 0 8px #00bfff; }
.led-female { color: #ff69b4; border-color: #ff69b4; text-shadow: 0 0 8px #ff69b4; }
.led-vs { font-family: 'Orbitron'; color: #ffff00; font-size: 22px; text-align: center; text-shadow: 0 0 15px #ffff00; margin: 10px 0; }
</style>"""

# ============================================================
# CSS 주입 함수 (JavaScript 사용)
# ============================================================

def inject_css(css_content):
    """JavaScript를 통해 CSS를 부모 문서에 주입"""
    # style 태그 제거 (순수 CSS만 추출)
    css_clean = css_content.replace('<style>', '').replace('</style>', '').strip()
    # JavaScript 문자열에서 특수문자 이스케이프
    css_escaped = css_clean.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

    js_code = """
    <script>
        (function() {
            var existingStyle = window.parent.document.getElementById('custom-css');
            if (existingStyle) {
                existingStyle.remove();
            }
            var style = document.createElement('style');
            style.id = 'custom-css';
            style.textContent = `""" + css_escaped + """`;
            window.parent.document.head.appendChild(style);
        })();
    </script>
    """
    components.html(js_code, height=0)

# ============================================================
# 헬퍼 함수
# ============================================================

def get_elapsed_minutes(start_time_str):
    """경과 시간 계산 (분)"""
    if not start_time_str:
        return 0
    try:
        start = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        elapsed = datetime.now() - start.replace(tzinfo=None)
        return max(0, int(elapsed.total_seconds() / 60))
    except:
        return 0

def render_magnet(member, mode="magnet"):
    """자석/칩 HTML 생성"""
    if not member:
        return ""

    name = member.get('name', '')
    birth = str(member.get('birth', ''))[-2:] if member.get('birth') else ''
    rank = member.get('rank', '') or ''
    gender = member.get('gender', '남')

    if mode == "magnet":
        cls = "magnet-male" if gender == "남" else "magnet-female"
        return f'<div class="magnet {cls}"><span class="magnet-name">{name}</span><span class="magnet-info">{birth}{rank}</span></div>'
    elif mode == "list":
        cls = "chip-male" if gender == "남" else "chip-female"
        return f'<span class="{cls}">{name}{birth}{rank}</span>'
    else:  # led
        cls = "led-male" if gender == "남" else "led-female"
        return f'<div class="led-player {cls}">{name}{birth}{rank}</div>'

def render_empty_slot(mode="magnet"):
    """빈 슬롯 HTML"""
    if mode == "magnet":
        return '<div class="magnet magnet-empty"><span style="font-size:10px;">빈자리</span></div>'
    return ""

# ============================================================
# 메인 라이브 상황실
# ============================================================

def show_live():
    # 세션 상태 초기화
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "magnet"
    if 'selected_session' not in st.session_state:
        st.session_state.selected_session = None
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()

    # 모드별 CSS (JavaScript 주입)
    mode = st.session_state.view_mode
    if mode == "magnet":
        inject_css(get_magnet_style())
    elif mode == "list":
        inject_css(get_list_style())
    else:
        inject_css(get_led_style())

    # ===== 상단 컨트롤 =====
    col1, col2, col3, col4 = st.columns([2, 1.5, 1, 0.5])

    with col1:
        st.markdown(f"## 🏸 {APP_NAME} 라이브")

    with col2:
        mode_sel = st.radio("모드", ["🧲자석", "📊리스트", "📺전광판"], horizontal=True, label_visibility="collapsed")
        mode_map = {"🧲자석": "magnet", "📊리스트": "list", "📺전광판": "led"}
        new_mode = mode_map.get(mode_sel, "magnet")
        if new_mode != st.session_state.view_mode:
            st.session_state.view_mode = new_mode
            st.rerun()

    with col3:
        sessions = db.get_sessions(limit=10)
        if sessions:
            opts = {f"{s['date']} {s.get('location', '')[:8]}": s['id'] for s in sessions}
            sel = st.selectbox("모임", list(opts.keys()), label_visibility="collapsed")
            st.session_state.selected_session = opts.get(sel)

    with col4:
        if st.button("🔄", help="새로고침"):
            db.clear_cache()
            st.rerun()

    # 모임 미선택 시
    if not st.session_state.selected_session:
        st.warning("모임을 선택하세요.")
        return

    session_id = st.session_state.selected_session
    session_info = db.get_session_by_id(session_id)

    if not session_info:
        st.error("모임 정보를 불러올 수 없습니다.")
        return

    # ===== 헤더 정보 =====
    stats = db.get_session_stats(session_id)
    st.markdown(f'''
    <div class="live-header">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div><b>🏟️ {session_info.get('location', '체육관')}</b> <span style="opacity:0.7; margin-left:10px;">{session_info.get('date', '')}</span></div>
            <div>참석 <b>{stats['total_participants']}</b>명 (남{stats['male_count']}/여{stats['female_count']}) | 경기 <b>{stats['total_matches']}</b>회</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ===== 모드별 렌더링 =====
    if mode == "magnet":
        render_magnet_mode(session_id, session_info)
    elif mode == "list":
        render_list_mode(session_id, session_info)
    else:
        render_led_mode(session_id, session_info)

    # ===== 자동 새로고침 (Streamlit 네이티브 방식) =====
    # 참고: st.rerun() 자동 새로고침은 streamlit-autorefresh 패키지 필요
    # 수동 새로고침 버튼으로 대체

# ============================================================
# 자석 모드
# ============================================================

def render_magnet_mode(session_id, session_info):
    """자석 모드 렌더링 - 최적화"""

    courts_num = session_info.get('courts_num', 4)
    court_names = str(session_info.get('courts_names', '1,2,3,4')).split(',')

    # 데이터 한 번에 로드
    all_participants = db.get_participants(session_id)

    # 상태별 분류
    by_status = {}
    for p in all_participants:
        s = p.get('status', 'checked_in')
        if s not in by_status:
            by_status[s] = []
        by_status[s].append(p)

    playing = by_status.get('playing', [])
    waiting = by_status.get('waiting', [])
    checked_in = by_status.get('checked_in', [])
    resting = by_status.get('resting', [])
    left_players = by_status.get('left', [])

    # 코트별 분류
    courts = {}
    for p in playing:
        c = p.get('court_num', 1)
        if c not in courts:
            courts[c] = []
        courts[c].append(p)

    # ===== 코트 영역 =====
    st.markdown("#### 🏟️ 코트")
    cols = st.columns(min(courts_num, 4))

    for idx, col in enumerate(cols):
        if idx >= len(court_names):
            break
        court_name = court_names[idx].strip()
        court_num = idx + 1
        players = courts.get(court_num, [])

        with col:
            is_active = len(players) > 0

            if is_active:
                # 경과 시간 계산
                start_time = players[0].get('game_start_time') if players else None
                elapsed = get_elapsed_minutes(start_time)

                html = f'''
                <div class="court-box">
                    <div class="court-title">{court_name}번</div>
                    <div class="court-timer">⏱️ {elapsed}분</div>
                    <div style="display:flex; justify-content:center; flex-wrap:wrap;">
                '''
                for p in players[:2]:
                    html += render_magnet(p.get('members', {}), "magnet")
                for _ in range(2 - len(players[:2])):
                    html += render_empty_slot("magnet")
                html += '</div><div class="vs-text">VS</div><div style="display:flex; justify-content:center; flex-wrap:wrap;">'
                for p in players[2:4]:
                    html += render_magnet(p.get('members', {}), "magnet")
                for _ in range(2 - len(players[2:4])):
                    html += render_empty_slot("magnet")
                html += '</div></div>'
                st.markdown(html, unsafe_allow_html=True)

                if st.button("⏹ 종료", key=f"end_{court_num}", use_container_width=True):
                    pids = [p['id'] for p in players]
                    db.release_from_court(pids)
                    st.rerun()
            else:
                st.markdown(f'''
                <div class="court-box" style="opacity:0.5;">
                    <div class="court-title">{court_name}번</div>
                    <div style="text-align:center; padding:30px 0; color:#81c784;">🏸 대기중</div>
                </div>
                ''', unsafe_allow_html=True)

                if st.button("▶ 배정", key=f"assign_{court_num}", use_container_width=True):
                    if len(checked_in) >= 4:
                        pids = [p['id'] for p in checked_in[:4]]
                        db.assign_to_court(pids, court_num)
                        st.rerun()
                    else:
                        st.warning("4명 미만")

    # ===== 대기열 =====
    st.markdown("---")
    st.markdown("#### ⏳ 대기열")

    q_cols = st.columns(4)
    for idx, col in enumerate(q_cols):
        q_num = idx + 1
        q_players = [p for p in waiting if p.get('queue_num') == q_num]

        with col:
            html = f'<div class="queue-box"><div class="queue-title">대기{q_num}</div><div style="display:flex; flex-wrap:wrap; justify-content:center;">'
            for p in q_players[:4]:
                html += render_magnet(p.get('members', {}), "magnet")
            for _ in range(4 - min(len(q_players), 4)):
                html += render_empty_slot("magnet")
            html += '</div></div>'
            st.markdown(html, unsafe_allow_html=True)

    # ===== 선수 풀 =====
    st.markdown("---")
    st.markdown("#### 👥 선수 풀")

    c1, c2, c3 = st.columns([2, 1, 1])

    with c1:
        st.markdown(f'<div class="pool-box"><div class="pool-title">✅ 출석완료 ({len(checked_in)}명)</div></div>', unsafe_allow_html=True)

        if checked_in:
            # 선택 상태를 세션에서 관리
            if 'selected_players' not in st.session_state:
                st.session_state.selected_players = set()

            # 간소화된 선택 UI
            selected = st.multiselect(
                "선수 선택",
                options=[p['id'] for p in checked_in],
                format_func=lambda x: db.format_player_name(next((p.get('members', {}) for p in checked_in if p['id'] == x), {})),
                label_visibility="collapsed"
            )

            if selected:
                bc1, bc2, bc3 = st.columns(3)
                with bc1:
                    if st.button(f"🎮 대기열 ({len(selected)})", use_container_width=True):
                        for pid in selected:
                            db.assign_to_queue(pid, 1)
                        st.rerun()
                with bc2:
                    if st.button("☕ 휴식", use_container_width=True):
                        for pid in selected:
                            db.update_participant_status(pid, 'resting')
                        st.rerun()
                with bc3:
                    if st.button("🚪 퇴장", use_container_width=True):
                        for pid in selected:
                            db.update_participant_status(pid, 'left')
                        st.rerun()
        else:
            st.info("출석 완료된 선수 없음")

    with c2:
        st.markdown(f'<div class="pool-box"><div class="pool-title">☕ 휴식 ({len(resting)}명)</div></div>', unsafe_allow_html=True)
        for p in resting[:5]:
            member = p.get('members', {})
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(db.format_player_name(member))
            with col_b:
                if st.button("↩", key=f"back_{p['id']}"):
                    db.update_participant_status(p['id'], 'checked_in')
                    st.rerun()

    with c3:
        st.markdown(f'<div class="pool-box"><div class="pool-title">🚪 퇴장 ({len(left_players)}명)</div></div>', unsafe_allow_html=True)
        for p in left_players[:5]:
            st.write(db.format_player_name(p.get('members', {})))

# ============================================================
# 리스트 모드
# ============================================================

def render_list_mode(session_id, session_info):
    """리스트 모드 - 최적화"""
    import pandas as pd

    courts_num = session_info.get('courts_num', 4)
    all_participants = db.get_participants(session_id)

    # 상태별 분류
    playing = [p for p in all_participants if p.get('status') == 'playing']
    waiting = [p for p in all_participants if p.get('status') == 'waiting']
    checked_in = [p for p in all_participants if p.get('status') == 'checked_in']
    resting = [p for p in all_participants if p.get('status') == 'resting']

    # 코트별 분류
    courts = {}
    for p in playing:
        c = p.get('court_num', 1)
        if c not in courts:
            courts[c] = []
        courts[c].append(p)

    # ===== 코트 현황 =====
    st.markdown("#### 🏟️ 코트 현황")

    court_data = []
    for i in range(1, courts_num + 1):
        players = courts.get(i, [])
        if players:
            team_a = ", ".join([db.format_player_name(p.get('members', {})) for p in players[:2]])
            team_b = ", ".join([db.format_player_name(p.get('members', {})) for p in players[2:4]])
            elapsed = get_elapsed_minutes(players[0].get('game_start_time'))
            court_data.append({"코트": f"{i}번", "Team A": team_a, "Team B": team_b, "경과": f"{elapsed}분", "상태": "🟢"})
        else:
            court_data.append({"코트": f"{i}번", "Team A": "-", "Team B": "-", "경과": "-", "상태": "⚪"})

    st.dataframe(pd.DataFrame(court_data), use_container_width=True, hide_index=True)

    # 코트 버튼
    btn_cols = st.columns(courts_num)
    for idx, col in enumerate(btn_cols):
        court_num = idx + 1
        with col:
            if court_num in courts:
                if st.button(f"⏹ {court_num}번 종료", key=f"end_l_{court_num}", use_container_width=True):
                    pids = [p['id'] for p in courts[court_num]]
                    db.release_from_court(pids)
                    st.rerun()
            else:
                if st.button(f"▶ {court_num}번 배정", key=f"start_l_{court_num}", use_container_width=True):
                    if len(checked_in) >= 4:
                        pids = [p['id'] for p in checked_in[:4]]
                        db.assign_to_court(pids, court_num)
                        st.rerun()

    # ===== 출석 완료 =====
    st.markdown("---")
    st.markdown(f"#### ✅ 출석완료 ({len(checked_in)}명)")

    if checked_in:
        data = [{"#": i+1, "선수": db.format_player_name(p.get('members', {})), "성별": p.get('members', {}).get('gender', ''), "급수": p.get('members', {}).get('rank', '')} for i, p in enumerate(checked_in)]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True, height=200)

    # ===== 휴식/퇴장 =====
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"#### ☕ 휴식 ({len(resting)}명)")
        for p in resting:
            st.write(f"• {db.format_player_name(p.get('members', {}))}")
    with c2:
        left_p = [p for p in all_participants if p.get('status') == 'left']
        st.markdown(f"#### 🚪 퇴장 ({len(left_p)}명)")
        for p in left_p:
            st.write(f"• {db.format_player_name(p.get('members', {}))}")

# ============================================================
# 전광판 모드
# ============================================================

def render_led_mode(session_id, session_info):
    """전광판 모드 - 최적화"""

    courts_num = session_info.get('courts_num', 4)
    all_participants = db.get_participants(session_id)

    playing = [p for p in all_participants if p.get('status') == 'playing']
    waiting = [p for p in all_participants if p.get('status') == 'waiting']
    checked_in = [p for p in all_participants if p.get('status') == 'checked_in']

    courts = {}
    for p in playing:
        c = p.get('court_num', 1)
        if c not in courts:
            courts[c] = []
        courts[c].append(p)

    # ===== 코트 =====
    cols = st.columns(min(courts_num, 4))

    for idx, col in enumerate(cols):
        court_num = idx + 1
        players = courts.get(court_num, [])

        with col:
            if players:
                elapsed = get_elapsed_minutes(players[0].get('game_start_time'))
                html = f'''
                <div class="led-court">
                    <div class="led-title">COURT {court_num}</div>
                    <div class="led-timer">{elapsed:02d}:00</div>
                '''
                for p in players[:2]:
                    html += render_magnet(p.get('members', {}), "led")
                html += '<div class="led-vs">⚡ VS ⚡</div>'
                for p in players[2:4]:
                    html += render_magnet(p.get('members', {}), "led")
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)

                if st.button("END", key=f"led_end_{court_num}", use_container_width=True):
                    pids = [p['id'] for p in players]
                    db.release_from_court(pids)
                    st.rerun()
            else:
                st.markdown(f'''
                <div class="led-court" style="opacity:0.4;">
                    <div class="led-title">COURT {court_num}</div>
                    <div style="text-align:center; padding:40px 0; color:#00ff00;">READY</div>
                </div>
                ''', unsafe_allow_html=True)

    # ===== 대기열 =====
    st.markdown("---")
    st.markdown('<div style="color:#ff9800; font-family:Orbitron; font-size:18px; text-shadow:0 0 10px #ff9800;">▶ NEXT</div>', unsafe_allow_html=True)

    q_cols = st.columns(4)
    for idx, col in enumerate(q_cols):
        q_players = waiting[idx*4:(idx+1)*4]
        with col:
            html = f'<div style="background:#0a0a0a; border:2px solid #ff9800; padding:10px; margin:5px;">'
            html += f'<div style="color:#ff9800; font-family:Orbitron; font-size:14px;">WAIT #{idx+1}</div>'
            if q_players:
                for p in q_players:
                    m = p.get('members', {})
                    color = "#00bfff" if m.get('gender') == '남' else "#ff69b4"
                    html += f'<div style="color:{color}; padding:3px; font-size:13px;">{db.format_player_name(m)}</div>'
            else:
                html += '<div style="color:#333;">EMPTY</div>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)

    # ===== 대기 선수 =====
    st.markdown("---")
    names = " | ".join([db.format_player_name(p.get('members', {})) for p in checked_in[:15]])
    st.markdown(f'''
    <div style="background:#050505; border:1px solid #333; padding:12px;">
        <div style="color:#666; font-family:Orbitron; font-size:12px;">STANDBY ({len(checked_in)})</div>
        <div style="color:#00ff00; margin-top:8px; font-size:13px;">{names}</div>
    </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    show_live()
