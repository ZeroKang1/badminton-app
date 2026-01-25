-- 2026.01.25 
-- DROP TABLE IF EXISTS sessions;
-- 1. 회원 정보 테이블
CREATE TABLE members (
    id int8 GENERATED ALWAYS AS IDENTITY (START WITH 101) PRIMARY KEY,
    name TEXT NOT NULL,
    group_name TEXT, -- 여민소, 민턴크루 등
    gender TEXT CHECK (gender IN ('남', '여')),
    rank TEXT, -- 자당 A, B, C, D, 초심
    phone TEXT,
    memo TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- 2. 모임 정보 테이블
CREATE TABLE sessions (
    id int8 GENERATED ALWAYS AS IDENTITY (START WITH 101) PRIMARY KEY,
    title TEXT NOT NULL,
    location TEXT, -- 영등포체육관, 계남체육관 등
    date DATE DEFAULT CURRENT_DATE,
    start_time TIME,
    end_time TIME,
    courts_num INT DEFAULT 1,
    memo TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 참석자 명단 테이블 (고정 파트너 로직 포함)
CREATE TABLE participants (
    id int8 GENERATED ALWAYS AS IDENTITY (START WITH 101) PRIMARY KEY,
    session_id int8 REFERENCES sessions(id) ON DELETE CASCADE,
    member_id int8 REFERENCES members(id) ON DELETE CASCADE,
    status TEXT DEFAULT '정상', -- 정상, 늦참, 조퇴, 대기
    entry_time TIME,
    fixed_partner_id int8 REFERENCES members(id), -- 고정 파트너
    fixed_game_count INT DEFAULT 0, -- 고정 파트너와 칠 게임 수
    memo TEXT
);

-- 4. 경기 대진표 테이블
CREATE TABLE matches (
    id int8 GENERATED ALWAYS AS IDENTITY (START WITH 101) PRIMARY KEY,
    session_id int8 REFERENCES sessions(id) ON DELETE CASCADE,
    match_order INT NOT NULL,
    court_num INT,
    predicted_start TIME, -- 예상 투입 시간
    actual_start TIMESTAMPTZ, -- 실제 경기 시작
    actual_end TIMESTAMPTZ, -- 실제 경기 종료
    
    -- 선수 배정 (단식/복식 모두 대응 가능하도록 4명까지)
    team_a_p1 int8 REFERENCES members(id),
    team_a_p2 int8 REFERENCES members(id),
    team_b_p1 int8 REFERENCES members(id),
    team_b_p2 int8 REFERENCES members(id),
    
    score_a INT DEFAULT 0,
    score_b INT DEFAULT 0,
    memo TEXT
);

create table match_results (
  id int8 GENERATED ALWAYS AS IDENTITY (START WITH 101) PRIMARY KEY,
  session_id int8 references sessions(id),
  court_name text,
  team_a_players text[], -- ['홍길동', '김철수']
  team_b_players text[],
  score_a int,
  score_b int,
  start_time text,
  end_time text,
  created_at timestamp with time zone default now()
);