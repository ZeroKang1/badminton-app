# 배드민턴 모임 운영 관리 시스템 인수인계 문서 (Handover Docs)

**배드민턴 클럽 운영 관리 시스템 인수인계 문서 (Handover Docs)**

본 문서는 배드민턴의 효율적인 모임 운영과 실시간 상황실 관리를 위해 개발된 시스템의 기술 명세 및 운영 가이드를 담고 있습니다.

**1. 시스템 개발 취지**
• **운영 효율화:** 수기로 관리하던 회원 명단과 참가 접수를 디지털화하여 운영진의 업무 부담 경감.
• **실시간 투명성:** 코트 배정 및 대기 순번을 실시간으로 공유하여 회원 간의 불필요한 오해 방지.
• **데이터 자산화:** 모임 이력 및 회원 활동 데이터를 축적하여 향후 클럽 운영 전략 수립에 활용.

**2. 시스템 환경 설정 (Stack)**
• **Frontend/App Framework:** [Streamlit](https://streamlit.io/) (Python 기반 웹 프레임워크)
• **Backend/Database:** [Supabase](https://supabase.com/) (PostgreSQL 기반 BaaS)
• **Language:** Python 3.12+
• **Library:**
    ◦ `pandas`: 데이터 처리 및 분석
    ◦ `st-supabase-connection`: Supabase 연동
    ◦ `xlsxwriter`: 엑셀 파일 생성 및 다운로드

**3. 화면별 요구사항 및 주요 기능화면명주요 요구사항핵심 기능구현 특징📊 회원명단 관리**엑셀 스타일의 슬림한 UI, 빠른 검색 및 편집회원 등록/수정/삭제, 엑셀 일괄 업로드파스텔톤 UI, 행간 최소화, ID 툴팁 제공**📅 모임 생성**날짜, 장소, 소속 그룹별 모임 개설모임 제목, 시간, 코트 정보 입력 및 관리`sessions` 테이블 연동, Not-Null 제약 준수**📝 참가 접수**소속 그룹원만 필터링하여 신속한 체크성함+생년+급수 기반 체크박스 접수`participants` 테이블 연동, 그룹 자동 필터링**📺 실시간 상황실**실시간 코트 현황 및 대기열 표기참석자 리스트업 및 코트 배정 현황 출력(개발 예정) 실시간 데이터 스트리밍 연동

**4. 소스 코드 구조 및 관리
📂 Directory Structure**
• `app.py`: 시스템의 메인 엔트리 포인트 (내비게이션 관리)
• `admin_page.py`: 운영진 관리 메뉴 (회원/모임/접수 탭 통합)
• `match_manager.py`: 참가 접수 및 그룹 필터링 전용 로직
• `database.py`: Supabase CRUD 공통 함수 정의
• `requirements.txt`: 라이브러리 의존성 목록
**🛠 소스 관리 전략**
• **Version Control:** Git을 통한 형상 관리 (GitHub/GitLab)
[https://github.com/ZeroKang1/badminton-app](https://github.com/ZeroKang1/badminton-app)
메일계정: zerokang@gmail.com

• **Commit Message 규칙:**
    ◦ `Feat`: 새로운 기능 추가
    ◦ `Fix`: 버그 수정 (예: DB 컬럼명 매칭 수정)
    ◦ `Style`: 디자인 변경 (CSS 수정 등)

**5. 배포 및 운영 전략**
• **Platform:** Streamlit Community Cloud 또는 Docker 기반 자체 배포.
• **Database Security (RLS):** Supabase의 Row Level Security를 활성화하여 익명 사용자의 데이터 수정을 차단.
• **API Key 관리:** `.streamlit/secrets.toml` 또는 환경 변수를 통해 API URL과 Key를 보안 관리.

**6. 향후 발전 방안 (Roadmap)**
1. **자동 대진표 알고리즘:** 급수(A~D)와 휴식 시간을 고려한 최적의 매치메이킹 로직 구현.
2. **모바일 최적화:** 현장 운영진이 스마트폰으로 코트 옆에서 즉시 접수 가능한 반응형 UI 강화.
3. **활동 통계 대시보드:** 월별 참석률, 회원별 게임 수 등 통계 지표 시각화.
4. **카카오톡 알림톡 연동:** 모임 생성 및 코트 배정 시 자동 알림 발송 기능.