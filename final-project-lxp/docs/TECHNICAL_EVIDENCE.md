# 기술 설계 근거

## 빠른 확인

- [BasePage 코드](../pages/base_page.py) · [디버깅 Helper](../pages/debug_helper.py)
- [BasePage 기능 판단 기준](../pages/BASE_PAGE_FUNCTION_REFERENCE.md)
- [학습자 Page Object](../pages/learner/) · [교육자 Page Object](../pages/educator/) · [공용 로그인](../pages/login_page.py)
- [UI FULL](../ci/Jenkinsfile.ui) · [UI SMOKE](../ci/Jenkinsfile.ui-smoke)
- [실행 결과](./TEST_RESULTS.md)
- [LXP 프로젝트 소개](../README.md)

## BasePage 개선 목표

BasePage는 요소 탐색·상태 대기·클릭·입력·스크롤처럼 특정 화면에 종속되지 않고 반복되는 Selenium 동작을 담당합니다. 과목 선택, 게시글 작성, 일정 저장처럼 화면별 흐름과 완료 조건이 필요한 기능은 각 Page Object에 두었습니다.

- WebDriver와 timeout 관리
- 요소의 DOM 생성·표시·활성 상태 대기
- 표시된 중복 DOM 조회
- 입력과 클릭 전 viewport 확인
- 제한적인 Stale·클릭 차단 재조회
- 동적 화면의 위치·가림 상태 확인
- 공통 스크롤

기존 WebElement는 이미 선택한 요소를 그대로 조작하지만, Locator 기반 공통 메서드는 동작 시점에 DOM에서 요소를 다시 찾습니다. 동적 목록이 다시 렌더링되거나 항목 순서가 바뀌면 처음 선택한 요소와 다른 요소를 가리킬 수 있습니다.

## 1차 프로젝트와 비교

`pause_for_debugging()`은 `debug_helper.py`로 책임을 이동했으므로 비교 대상에서 제외했습니다.

| 구분 | 1차 프로젝트 | 최종 프로젝트 |
| --- | ---: | ---: |
| 비교한 공용 메서드 | 21 | 14 |
| 실제 사용 메서드 | 15 | 14 |
| 적용한 Page Object | 5 | 12 |
| 미사용 메서드 | 6 | 0 |

비교 결과, 1차 프로젝트에서 실제 사용하지 않았던 메서드를 정리하고 남은 14개를 최종 프로젝트의 Page Object에서 모두 사용했습니다.

## 역할별 사용

학습자 Page Object 5개에서는 다음 BasePage 메서드 9종을 사용했습니다.

```text
click
click_when_position_stable
fill_text
find_elements_visible
find_optional_visible
open_url
scroll_element_into_view
wait_for_first_visible
wait_for_visible
```

교육자 Page Object 6개에서는 다음 BasePage 메서드 13종을 사용했습니다.

```text
click
click_when_position_stable
click_with_javascript
fill_text
find_elements_visible
find_optional_visible
get_text
open_url
scroll_element_into_view
wait_for_clickable
wait_for_invisible
wait_for_present
wait_for_visible
```

두 역할에서 함께 사용한 메서드는 다음 8개입니다.

```text
click
click_when_position_stable
fill_text
find_elements_visible
find_optional_visible
open_url
scroll_element_into_view
wait_for_visible
```

## 디버깅 책임 분리

`pause_for_debugging()`은 화면을 조작하거나 상태를 확인하는 공통 기능이 아니라, 실행 장면을 보기 위해 잠시 멈추는 디버깅 기능입니다. BasePage의 역할과 달라 `debug_helper.py`의 독립 함수로 옮겼습니다.

## 기능 판단 문서

`BASE_PAGE_FUNCTION_REFERENCE.md`에는 현재 기능의 반환값·실패 동작·유지 근거와 다음 프로젝트에서의 재도입 조건을 기록했습니다.

- 필수 요소는 `TimeoutException`을 전달
- 없어도 정상인 선택 요소만 `None` 반환
- 성공한 클릭은 반복하지 않음
- Stale 또는 일시적 클릭 차단에서만 제한적으로 재조회
- 화면 의미·DOM 순서·특정 레이아웃에 의존하면 Page Object에 유지
- 두 개 이상의 Page에서 같은 기술 동작이 반복될 때 공통화 검토

## UI CI 설계

### 초기 구축 판단과 최종 환경

초기에는 약 2주의 일정과 기존 Windows 브라우저 테스트 환경을 고려해 개인 PC의 Jenkins를 Tailscale 장치 공유로 팀원에게 제공했습니다. 모바일 Wi-Fi를 끈 외부 네트워크에서 Tailscale 연결 시 접속되고, 해제하면 접속되지 않는지 확인했습니다.

이 구성에서는 외부 서비스의 Webhook을 직접 받는 데 제약이 있어 Poll SCM을 사용하는 방향으로 검토했습니다. 이후 기관이 Ubuntu VM을 제공하면서 Jenkins 환경을 전환했습니다. 따라서 초기 Windows·Tailscale 구성과 최종 Ubuntu VM의 MR 연동은 서로 다른 시점의 구성입니다.

최종 VM에서는 Jenkins 수신 주소와 서비스 설정을 점검해 외부 접속을 확인하고 팀원 계정·권한을 설정했습니다.

[개인 구축·회고 기록 — 0828·0830·0903 항목](https://app.notion.com/p/3c8ebccabd678021be35c5b147396282)

### 최종 UI 파이프라인

- FULL과 SMOKE를 목적별 Jenkins Job으로 분리
- worker 2개와 `--dist=loadfile`로 파일 단위 병렬 실행
- MR에는 핵심 탐색 6개만 연결
- FULL은 전체 회귀가 필요할 때 수동 실행
- 테스트 판정과 결과 게시 단계를 분리
- 실행 전 이전 결과를 정리해 현재 Allure 결과만 생성
- 테스트 실패 시에도 JUnit·Allure·로그·screenshot 보존

`Jenkinsfile.ui`는 UI FULL 초기 구축 이후 팀원의 결과 연동이 추가된 공동 파일입니다.
