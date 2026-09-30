# TEAM SYNC LXP QA 자동화

클래스·과목·일정·게시판을 제공하는 온라인 학습 플랫폼의 UI 회귀 테스트를 자동화한 팀 프로젝트입니다. 학습자 UI 자동화와 Jenkins UI CI를 담당하고, 학습자·교육자 코드에서 함께 사용할 BasePage와 협업 기준을 정리했습니다.

- 기간: 2026.08.26–2026.09.11
- 환경: LXP Dev QA 전용 SANDBOX
- 개인 역할: 학습자 UI 자동화·Jenkins UI CI·공용 코드와 협업 기준 정리
- 기술: Python, pytest, Selenium, Jenkins, GitLab MR, Allure, JUnit, pytest-xdist

## 바로가기

| 구분 | 링크 |
| --- | --- |
| 코드 | [BasePage](./pages/base_page.py) · [학습자 Page Object](./pages/learner/) · [교육자 Page Object](./pages/educator/) · [UI 테스트 57개](./tests/) |
| 기술 기록 | [문제 해결 사례](./docs/CASE_STUDIES.md) · [기술 설계 근거](./docs/TECHNICAL_EVIDENCE.md) · [실행 결과](./docs/TEST_RESULTS.md) |
| CI·협업 | [FULL](./ci/Jenkinsfile.ui) · [SMOKE](./ci/Jenkinsfile.ui-smoke) · [공용 작업 기준](./AGENTS.md) · [TEAM SYNC 공유 사항](https://app.notion.com/p/TEAM-SYNC-3cfebccabd6780698807f9eec41afd73) |
| 실행 영상 | [Selenium UI FULL 및 Jenkins 연동](https://www.youtube.com/watch?v=RmZ1B9MWsd8) |

## 핵심 결과와 담당 범위

| 구분 | 내용 |
| --- | --- |
| 개인 담당 범위 | 학습자 테스트 케이스 149건 · 자동화 케이스 38건 |
| 개인 구현 | 학습자 Page Object 5개 · pytest 테스트 함수 24개 |
| 팀 UI FULL | 학습자 24개 + 교육자 33개, 총 57개 함수 |
| Jenkins FULL #17 | 54 passed / 1 failed / 2 broken |
| Jenkins SMOKE #25 | 핵심 탐색 흐름 6개 passed |

자동화 케이스 38건은 검증한 TC의 수이고, pytest 함수 24개는 실제 실행되는 테스트 함수의 수입니다. 같은 사용자 흐름과 화면 상태의 여러 TC는 하나의 함수로 묶어 검증했습니다. FULL·SMOKE 결과는 학습자와 교육자를 포함한 팀 UI 실행 기록입니다.

## BasePage: 팀 UI 코드의 공통 동작 기준

**학습자·교육자 Selenium 코드가 같은 대기·조작 기준을 사용하도록 공통 기능을 정리했습니다.** HELPY에서 경험한 POM을 바탕으로 반복 동작과 화면별 책임을 다시 정리했습니다.

| 계층 | 책임 |
| --- | --- |
| Test | 사용자 흐름 실행 · 최종 결과 assert |
| Page Object | 화면별 Locator · 사용자 동작 · 화면 정보 조회 |
| BasePage | 공통 요소 탐색 · 상태 대기 · 클릭 · 입력 · 스크롤 |

- 여러 화면에서 같은 규칙으로 반복되는 Selenium 동작만 공통화했습니다.
- 선택한 목록 항목이나 화면 문맥이 중요한 동작은 각 Page Object에 유지했습니다.
- 공용 메서드를 변경할 때 기존 호출부·반환값·예외 처리에 미치는 영향을 함께 확인했습니다.
- 본인 학습자 코드뿐 아니라 팀원의 교육자 Selenium 코드에도 적용했습니다.

## 문제를 분석하고 검증 기준을 개선한 과정

| 사례 | 판단과 대응 |
| --- | --- |
| 로그인 재인증 화면 | 늦게 발생하는 화면 전환에 대응해 재인증 처리와 원래 클래스 화면 복귀까지 완료 조건으로 구성 |
| 게시글 등록 결과 검증 | 실제 도착한 상세 화면에서 고유 제목과 본문을 완전 일치로 확인하도록 검증 위치 수정 |
| Headless 일정 수정 실패 | 로그·화면·DOM 속성을 비교해 실패 단계를 좁히고, 관찰한 차이와 미확정 원인을 구분 |

## 협업 구조와 공용 기준

역할별 UI 코드를 같은 구조에서 작성할 수 있도록 환경변수 사용 위치, Page Object·Test의 역할, fixture·marker 사용법을 Notion에 정리했습니다. Python·Git·Poetry 명령어와 POM 구조를 이해하기 위한 클래스 기본 자료도 함께 공유했습니다.

이후 공용 fixture 충돌을 조정하고, 필수·선택 동작의 예외 처리와 공용 파일 변경 기준을 AGENTS.md 등에 정리했습니다.

## UI CI: 빠른 변경 확인과 전체 회귀 분리

초기에는 짧은 일정과 기존 Windows 테스트 환경을 고려해 Tailscale 기반 Jenkins를 구성했습니다. 외부 접속과 Webhook 수신 제약을 확인했고, 이후 기관에서 제공한 Ubuntu VM으로 전환했습니다. 아래 결과는 최종 Ubuntu VM 환경의 UI CI 기준입니다.

| 구분 | UI SMOKE | UI FULL |
| --- | --- | --- |
| 목적 | MR 변경 후 핵심 경로 확인 | 전체 UI 회귀 확인 |
| 실행 조건 | MR 생성·갱신 시 자동 실행 | 전체 회귀가 필요할 때 수동 실행 |
| 범위 | 생성·수정·삭제를 제외한 탐색 흐름 6개 | 학습자·교육자 합계 57개 |
| 대표 pytest 실행 시간 | #25: 106.30초 | #17: 924.61초, 약 15분 |

두 Job은 worker 2개와 파일 단위 병렬 분배를 사용합니다. SMOKE 6개는 FULL 57개 중 변경 후 빠르게 확인할 핵심 탐색 흐름입니다.

실패 시 runtime·traceback·pytest 로그, 화면, JUnit·Allure를 남겨 실패 단계를 확인할 수 있게 했습니다. UI 파이프라인 초기 구축과 실행 구조를 담당했으며, 이후 팀원이 추가한 Google Sheets·대시보드 연동은 공동 작업으로 구분합니다.

## HELPY에서 LXP로 이어진 개선

| HELPY에서 확인한 개선 과제 | LXP에서 적용한 내용 |
| --- | --- |
| 화면 조작과 기대 결과 판정 구분 | 상세 화면의 제목·본문을 Test에서 assert |
| 실패 당시 상태를 확인할 자료 확보 | 로그·traceback·실패 화면·Allure 연결 |
| 프로젝트 초기에 공통 작성 기준 공유 | Notion·AGENTS.md에 구조와 예외 기준 정리 |

[HELPY README](../ai_helpy_chat/README.md)는 당시 구현과 한계를 보존한 기록입니다. 위 내용은 후속 프로젝트인 LXP에서 적용한 개선입니다.

## 프로젝트 구조

```text
final-project-lxp/
├─ pages/
│  ├─ base_page.py
│  ├─ login_page.py
│  ├─ learner/
│  └─ educator/
├─ tests/
│  ├─ conftest.py
│  ├─ learner/       # 24개 테스트 함수
│  └─ educator/      # 33개 테스트 함수
├─ ci/               # Jenkins UI FULL·SMOKE
├─ docs/             # 문제 해결·기술 설계·실행 결과
└─ AGENTS.md         # 공용 작업 기준
```

학습자·교육자 Page Object와 UI FULL의 57개 테스트 함수를 같은 구조에서 확인할 수 있습니다. 개인 담당 범위는 위 표와 같으며, 교육자 코드는 팀 UI FULL 구성과 BasePage의 공용 적용을 확인하기 위해 함께 수록했습니다. 계정값은 환경변수에서 불러옵니다.

## 확인된 한계

| 항목 | 확인 결과 |
| --- | --- |
| Jenkins UI FULL #17 | 57개 중 54 passed, TC-009 failed, TC-015·112 broken |
| 로컬·Headless 차이 | TC-112는 로컬에서 통과했으며, Headless에서는 날짜 입력 속성과 달력 요소가 다르게 나타남 |
