# QA Automation Portfolio

UI 자동화를 구현하며 화면 상태와 실패 로그를 분석하고, 공통 코드와 협업 기준을 팀 작업에 적용한 QA 포트폴리오입니다.

AI HELPY CHAT에서 상태 기반 대기와 POM 구조를 경험한 뒤, TEAM SYNC LXP에서 최종 결과 검증·실패 증적 수집·공용 작성 기준으로 발전시켰습니다.

## Projects

### AI Helpy Chat UI 자동화

AI 대화 서비스의 새 대화·AI 응답·사이드바·에이전트 만들기를 Firefox와 Selenium으로 자동화한 프로젝트입니다.

- 주요 경험: 숨겨진 중복 DOM 탐색, 응답 상태 기반 대기, 내부 컨테이너 스크롤, POM 구조 적용
- 대표 결과: TC 항목 72개 중 62개 자동화 · pytest 시나리오 4개 통과
- 현재 상태: 개발 서버 종료 · 코드·실행 로그·영상 기록 공개
- [프로젝트 상세](./ai_helpy_chat/README.md)
- [LXP에서 이어진 개선](./final-project-lxp/README.md#helpy에서-lxp로-이어진-개선)

### TEAM SYNC LXP QA 자동화

클래스·과목·일정·게시판을 제공하는 온라인 학습 플랫폼의 UI 회귀 테스트를 자동화한 팀 프로젝트입니다.

- 기간: 2026.08.26–2026.09.11
- 핵심 기여: 학습자 UI 자동화, Jenkins UI FULL·SMOKE, BasePage와 공용 협업 기준 정리
- 주요 경험: 로그인 재인증 화면 처리, 게시글 최종 결과 검증, 로컬·Headless 실패 증적 비교
- 대표 결과: 학습자 자동화 케이스 38건 · 팀 UI 테스트 함수 57개
- 대표 실행: FULL 54 passed / 1 failed / 2 broken · SMOKE 6 passed
- 기술: Python, pytest, Selenium, Jenkins, GitLab MR, Allure, JUnit, pytest-xdist
- [프로젝트 상세](./final-project-lxp/README.md)
- [자동화 실행 영상](https://www.youtube.com/watch?v=RmZ1B9MWsd8)
