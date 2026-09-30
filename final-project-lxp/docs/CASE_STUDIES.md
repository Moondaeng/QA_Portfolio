# 문제 해결 사례

[프로젝트 소개](../README.md)

## 1. 로그인 재인증 화면 전환 안정화

**근거:** [개인 분석 기록 — 0831·0903 재인증](https://app.notion.com/p/3c8ebccabd678021be35c5b147396282) · [재인증 처리](../pages/login_page.py#L117-L179) · [학습자 로그인·복귀 흐름](../tests/conftest.py#L414-L460)

**문제:** 로그인과 클래스 화면 표시가 끝난 것처럼 보인 뒤 비밀번호 재인증 화면으로 늦게 이동했습니다. 호출 시점에 즉시 확인하는 방식은 뒤늦은 전환을 놓쳤고, 인증이 끝나지 않은 브라우저를 사용하는 후속 테스트도 실패할 수 있었습니다.

**판단과 변경:** 요소 대기 시간만 늘리기보다 인증 흐름의 완료 조건과 책임을 정리했습니다.

- 클래스룸 또는 재인증 화면 중 하나가 확인될 때까지 대기
- 재인증 폼 표시·제출·URL 이탈·원래 클래스 화면 복귀를 완료 조건으로 구성
- 개별 테스트에 흩어진 처리를 공용 LoginPage와 로그인 fixture로 통합
- 일반 로그인 실패를 재인증으로 우회하지 않고, 인증 실패와 화면 전환 실패를 구분하도록 기록

**확인 결과:** 분석 기록에서 재인증 발생 위치와 후속 테스트에 미치는 영향을 비교했습니다. 재인증 직후 원래 클래스에 도착했는지까지 확인하도록 흐름을 개선했고, 이후 발생한 UI 실패는 인증과 다른 단계의 문제로 구분할 수 있었습니다.

재인증 감지와 처리, 클래스 진입 후 복귀 조건을 위 코드에서 함께 확인할 수 있습니다.

## 2. 게시글 등록: 실제 도착한 상세 화면에서 결과 검증

**근거:** [개인 분석 기록 — 0908 검증 정확도 개선](https://app.notion.com/p/3c8ebccabd678021be35c5b147396282) · [게시글 생성 결과 검증](../tests/learner/test_p0_board.py#L99-L123) · [상세 제목·본문 조회](../pages/learner/board_page.py#L181-L196)

**문제:** 게시글 등록 후 목록에서 생성 글을 찾다가 Timeout이 발생했습니다.

**판단과 변경:** 등록 후 실제로 도착한 화면은 목록이 아닌 게시글 상세였습니다. 기능 처리 실패와 검증 위치 오류를 구분하고, 상세 영역의 제목·본문이 입력값과 일치하는지 확인하도록 변경했습니다.

- 실행마다 고유 제목을 만들어 이전 실행 데이터와 구분
- `wait_for_post_detail()`에서 대상 상세 영역을 기다린 뒤 제목·본문 조회
- Test에서 제목과 본문을 각각 완전 일치로 assert

현재 공개된 테스트의 핵심 검증은 다음과 같습니다. 실패 메시지 등 주변 코드는 생략한 발췌입니다.

```python
created_title, created_content = board.wait_for_post_detail(unique, content)

assert created_title == unique
assert created_content == content
```

**확인 범위:** 클릭이나 함수 반환만으로 통과시키지 않고, 사용자가 확인하는 최종 화면을 검증하도록 바꿨습니다. 제품 동작은 완료됐지만 테스트가 잘못된 화면에서 결과를 찾던 검증 오류를 수정한 사례입니다.

## 3. Headless CI 실패와 환경 차이 분석

**근거:** [개인 분석 기록 — 0909 Headless](https://app.notion.com/p/3c8ebccabd678021be35c5b147396282) · [로컬·Jenkins 결과 비교](./TEST_RESULTS.md#로컬-windows-ui-full) · [TC-112 날짜 유지 검증](../tests/educator/test_p1_lesson_date.py#L46-L95) · [달력 날짜 선택](../pages/educator/lesson_page.py#L289-L325)

**문제:** 로컬 headed Chrome에서 통과한 교육자 TC-112가 Jenkins Headless에서 실패했습니다.

**관찰과 대응:**

| 비교 대상 | 확인한 상태 |
| --- | --- |
| 로컬 | 날짜 입력칸의 readonly 미설정, 달력 요소 탐색, TC-112 passed |
| Headless | readonly=true, 기존 Locator의 달력 요소 not_found, TC-112 broken |
| 추가 확인 | 스크롤·위치 안정화 대기 뒤에도 같은 단계에서 실패 |

worker 로그, traceback, 실패 화면, JUnit·Allure를 함께 비교했습니다. 공통 요소 진단에는 `not_found`, `hidden`, `disabled`, `moving` 등의 상태를 남겨 실패 단계를 구분했습니다.

**확인 결과:** Headless에서 날짜 입력 속성과 달력 요소가 달라지고 같은 단계의 Timeout이 반복되는 것을 기록했습니다. 날짜 입력 방식 수정 결과와 이후에도 남은 환경별 탐색 실패를 별도로 구분했습니다.

## 4. 협업 구조와 공용 기준 정리

**근거:** [개인 분석 기록 — 협업과 회고](https://app.notion.com/p/3c8ebccabd678021be35c5b147396282) · [TEAM SYNC 공유 사항](https://app.notion.com/p/TEAM-SYNC-3cfebccabd6780698807f9eec41afd73) · [협업과 변경 기준](../AGENTS.md#협업과-변경-범위) · [필수 동작과 선택 조회](./EXCEPTION_HANDLING.md#필수-동작과-선택-조회)

역할별 UI 코드를 같은 구조에서 작성할 수 있도록 프로젝트 구조, 환경변수 사용 위치, Page Object와 Test의 역할, 로그인부터 클래스 진입까지의 흐름, fixture·marker 사용법을 정리했습니다. Python·Git·Poetry 명령어와 POM 이해를 위한 클래스 기본 자료도 Notion에 공유했습니다.

공용 `conftest.py` 충돌이 발생했을 때는 한쪽 파일 전체를 선택하지 않고 양쪽 fixture의 이름·scope·호출 방식을 비교해 병합했습니다. 이후 BasePage·LoginPage·fixture를 변경할 때 기존 호출부와 반환값·예외 처리에 미치는 영향을 함께 확인하도록 기준을 정리했습니다.

- 필수 동작의 실패는 예외로 전달하고, 없어도 정상인 선택 요소만 `None`·`False` 반환
- 화면별 동작은 Page Object, 최종 결과 검증은 Test에서 담당
- BasePage에는 여러 화면에서 같은 규칙으로 반복되는 Selenium 동작만 유지
- 폴더 위치를 고정된 담당자 소유권으로 보지 않고 작업 요청별 범위를 확인
