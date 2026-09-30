# UI 실행 결과와 SMOKE 선정 기준

## Jenkins Headless UI FULL #17

- 환경: Jenkins Ubuntu VM, Chrome Headless, 1920×880
- 실행: pytest-xdist worker 2개, 파일 단위 분배
- 결과: 57개 중 54 passed, 1 failed, 2 broken
- pytest 실행 시간: 924.61초, 약 15분
- 미통과: TC-009 failed, TC-015·112 broken
- 증적: JUnit, Allure result, worker log와 실패 screenshot의 결과 일치

## 로컬 Windows UI FULL

- 환경: Windows 11, Chrome headed
- 결과: 57개 중 55 passed, 2 failed
- 미통과: TC-009·015
- TC-112: passed

TC-112의 날짜 선택 방식을 수정한 뒤 로컬 단독 실행 9회가 통과했습니다. Jenkins Headless에서는 16회 중 9회 실패했으며, 날짜 입력 속성과 달력 요소가 로컬과 다르게 나타났습니다.

## Jenkins UI FULL 반복 실행

전체 UI 결과가 집계된 16회를 비교했습니다.

| 항목 | 결과 |
| --- | --- |
| 일반 실행 15회 | 14분 23초–16분 12초 · 평균 15분 23초 · 중앙값 15분 28초 |
| 환경 지연 #16 | 23분 59초 · ChromeDriver 응답 지연과 테스트 준비 오류 |
| TC-009 | 16/16회 실패 · 과목 목록 대신 이전 과목 상세 표시 |
| TC-015 | 16/16회 실패 · TC-009의 선행 화면 문제로 과목 선택 불가 |
| TC-112 | 9/16회 실패 · Jenkins 날짜 선택 단계 Timeout |
| 단발성 실패 | TC-030·055·058·061·078 각 1회 |

## UI 57개 실행 시간 비교

| 실행 방식 | 시간 |
| --- | ---: |
| 수동·브라우저 2개 | 약 36분 |
| 수동·브라우저 1개 | 약 38분 |
| 자동화·순차 | 약 25분 |
| 자동화·worker 2개 | 약 15분 |

worker 2개를 적용한 실행은 순차 자동화보다 약 40%, 수동 실행 평균 37분보다 약 59% 짧았습니다. 실행 후 JUnit·Allure·로그·실패 화면도 함께 남겼습니다.

## UI SMOKE 선정

MR마다 57개 전체 회귀를 실행하지 않고 상태 변경 위험이 낮은 주요 탐색 흐름을 분리했습니다.

| 역할 | TC | 확인 목적 |
| --- | --- | --- |
| 교육자 | TC-001 | 클래스룸 주요 메뉴 접근 |
| 학습자 | TC-018 | 전체 학습 과목 이동 |
| 학습자 | TC-037 | 과목 상세 주요 탭 확인 |
| 학습자 | TC-079 | 전체 수업 일정 이동 |
| 학습자 | TC-119 | 전체 게시판 이동 |
| 학습자 | TC-124 | 게시글 상세와 정보 확인 |

- Jenkins SMOKE #25: 6 passed, pytest 실행 시간 106.30초
- 별도 로컬 Allure 실행 구간: 약 90.34초. Jenkins 실행 시간과 구분합니다.

SMOKE 6개는 FULL 57개 중 MR 변경 후 빠르게 확인할 탐색 흐름입니다.

## 기록 기준과 해석

- Jenkins 빌드 번호와 결과는 확보한 실행 증적을 기준으로 합니다. 제출 보고서의 FULL #18 표기와 달리 확보된 Allure executor 메타데이터는 #17이므로 이 문서는 #17로 표시합니다.
- pytest 시간은 해당 빌드 콘솔의 실행 요약 기준입니다. Checkout·환경 준비·결과 게시를 포함한 Jenkins 빌드 전체 시간과 다릅니다.
- FULL의 54 passed / 1 failed / 2 broken은 Allure 상태 구분입니다. 같은 빌드의 pytest 콘솔은 3 failed / 54 passed로 요약하므로 도구별 상태 이름을 구분합니다.

### Jenkins 콘솔 발췌

보관된 Jenkins 실행 로그의 pytest 요약 원문입니다. 아래 시간은 빌드 전체 시간이 아닌 테스트 실행 구간입니다.

```text
UI FULL #17
=================== 3 failed, 54 passed in 924.61s (0:15:24) ===================

UI SMOKE #25
======================== 6 passed in 106.30s (0:01:46) =========================
```

[Headless 분석 과정](./CASE_STUDIES.md#3-headless-ci-실패와-환경-차이-분석) · [TC-112 테스트 코드](../tests/educator/test_p1_lesson_date.py) · [개인 분석 기록 — 0909 항목](https://app.notion.com/p/3c8ebccabd678021be35c5b147396282)

## 실행 영상

[Selenium UI FULL 병렬 테스트와 GitLab MR-Jenkins-Allure 자동화](https://www.youtube.com/watch?v=RmZ1B9MWsd8)
